import asyncio
import uuid
from datetime import datetime, timezone
from typing import Dict, List, Any, Callable
from ..models.schemas import Incident, AgentEvent, Escalation, IncidentResolution
from ..core.db import db
from .triage import triage_agent
from .investigation import investigation_agent
from .diagnosis import diagnosis_agent
from .action_planner import action_planner_agent
from .verification import verification_agent
from ..tools.registry import tool_registry
from ..tools.handlers import create_jira_escalation_ticket

class AgentOrchestrator:
    """Coordinates multi-agent pipeline execution and emits real-time events."""

    def __init__(self):
        self._listeners: Dict[str, List[asyncio.Queue]] = {}

    def subscribe(self, incident_id: str) -> asyncio.Queue:
        if incident_id not in self._listeners:
            self._listeners[incident_id] = []
        queue = asyncio.Queue()
        self._listeners[incident_id].append(queue)
        return queue

    def unsubscribe(self, incident_id: str, queue: asyncio.Queue):
        if incident_id in self._listeners:
            if queue in self._listeners[incident_id]:
                self._listeners[incident_id].remove(queue)
            if not self._listeners[incident_id]:
                del self._listeners[incident_id]

    async def _emit_event(self, incident: Incident, event: AgentEvent):
        incident.events.append(event)
        incident.updatedAt = datetime.now(timezone.utc)
        db.save_incident(incident)

        # Broadcast to any active SSE subscribers
        if incident.id in self._listeners:
            for q in self._listeners[incident.id]:
                await q.put(incident.model_dump(mode="json"))

    async def run_investigation_pipeline(self, incident_id: str):
        incident = db.get_incident_by_id(incident_id)
        if not incident:
            return

        # 1. TRIAGE STAGE
        incident.status = "investigating"
        triage_res = triage_agent.run(incident.description, incident.title)
        incident.category = triage_res.category
        incident.priority = triage_res.priority
        if incident.title == "New Incident" or not incident.title:
            incident.title = triage_res.title

        triage_event = AgentEvent(
            id=f"evt-{uuid.uuid4().hex[:6]}",
            timestamp=datetime.now(timezone.utc),
            agent="triage",
            status="completed",
            message=triage_res.message
        )
        await self._emit_event(incident, triage_event)
        await asyncio.sleep(0.3)

        # 2. INVESTIGATION STAGE
        evidence = investigation_agent.run(incident.description, incident.category)
        incident.evidence = evidence

        inv_event = AgentEvent(
            id=f"evt-{uuid.uuid4().hex[:6]}",
            timestamp=datetime.now(timezone.utc),
            agent="investigation",
            status="completed",
            message=f"Investigation gathered {len(evidence)} verified evidence items from Knowledge Base and live telemetry.",
            evidence=evidence
        )
        await self._emit_event(incident, inv_event)
        await asyncio.sleep(0.3)

        # 3. DIAGNOSIS STAGE
        incident.status = "diagnosed"
        diag = diagnosis_agent.run(incident.description, incident.category, evidence)
        incident.diagnosis = diag

        diag_event = AgentEvent(
            id=f"evt-{uuid.uuid4().hex[:6]}",
            timestamp=datetime.now(timezone.utc),
            agent="diagnosis",
            status="completed",
            message=f"Root cause diagnosed with {diag.confidence}% confidence: {diag.likelyCause}",
            diagnosis=diag
        )
        await self._emit_event(incident, diag_event)
        await asyncio.sleep(0.3)

        # 4. ACTION PLANNING STAGE
        action = action_planner_agent.run(incident.category, diag, evidence)
        incident.proposedAction = action

        if not action:
            # Escalation path
            incident.status = "escalated"
            escalation_reason = f"Automated resolution not feasible ({diag.uncertainty or 'Low diagnosis confidence'}). Escalated to Tier-2 IT Support."
            incident.escalationReason = escalation_reason
            
            # Generate escalation ticket
            tkt_res = create_jira_escalation_ticket(
                summary=f"Escalation: {incident.title}",
                priority="P1" if incident.priority in ["high", "critical"] else "P2",
                queue="Tier2_Support",
                diagnostic_notes=escalation_reason
            )
            incident.escalation = Escalation(
                reason=escalation_reason,
                targetQueue="Tier2_IT_Support",
                ticketId=tkt_res.get("ticket_id"),
                priority=incident.priority,
                diagnosticBrief=diag.likelyCause
            )

            escalate_event = AgentEvent(
                id=f"evt-{uuid.uuid4().hex[:6]}",
                timestamp=datetime.now(timezone.utc),
                agent="action_planner",
                status="failed",
                message=f"No safe automated tool available. {incident.escalationReason} Ref: {tkt_res.get('ticket_id')}"
            )
            await self._emit_event(incident, escalate_event)
            return

        # Check if approval is required
        if action.requiresApproval:
            incident.status = "pending_approval"
            incident.approvalRequired = True
            approval_event = AgentEvent(
                id=f"evt-{uuid.uuid4().hex[:6]}",
                timestamp=datetime.now(timezone.utc),
                agent="action_planner",
                status="processing",
                message=f"Proposed action '{action.tool}' requires human operator approval due to {action.riskLevel.upper()} risk classification.",
                action=action
            )
            await self._emit_event(incident, approval_event)
            return

        # If low risk and no approval required, proceed directly to execution
        plan_event = AgentEvent(
            id=f"evt-{uuid.uuid4().hex[:6]}",
            timestamp=datetime.now(timezone.utc),
            agent="action_planner",
            status="completed",
            message=f"Selected approved low-risk tool: '{action.tool}'. Executing remediation...",
            action=action
        )
        await self._emit_event(incident, plan_event)
        await asyncio.sleep(0.3)

        # 5. EXECUTION & VERIFICATION
        await self.execute_and_verify(incident)

    async def execute_and_verify(self, incident: Incident, simulate_failure: bool = False):
        if not incident.proposedAction:
            return

        incident.status = "executing"
        tool_name = incident.proposedAction.tool.split("(")[0]
        
        # Execute tool through allowlisted registry
        try:
            tool_registry.execute(tool_name)
        except Exception as e:
            pass # Continue to verification

        incident.status = "verifying"
        resolution = verification_agent.run(incident.proposedAction, simulate_failure=simulate_failure)
        incident.resolution = resolution

        await asyncio.sleep(0.3)

        if resolution.success:
            incident.status = "resolved"
            incident.approvalRequired = False
            verify_event = AgentEvent(
                id=f"evt-{uuid.uuid4().hex[:6]}",
                timestamp=datetime.now(timezone.utc),
                agent="verification",
                status="completed",
                message=f"Verification successful: {resolution.verificationMethod} confirmed healthy system state. {resolution.summary or ''} Incident resolved."
            )
            await self._emit_event(incident, verify_event)
        else:
            incident.status = "escalated"
            incident.approvalRequired = False
            incident.escalationReason = "Post-remediation verification check failed. Symptoms persist."
            tkt_res = create_jira_escalation_ticket(
                summary=f"Escalation after failed fix: {incident.title}",
                priority="P1",
                queue="Tier2_Support",
                diagnostic_notes=incident.escalationReason
            )
            incident.escalation = Escalation(
                reason=incident.escalationReason,
                targetQueue="Tier2_IT_Support",
                ticketId=tkt_res.get("ticket_id"),
                priority="high",
                diagnosticBrief="Automated fix failed verification probe."
            )
            verify_event = AgentEvent(
                id=f"evt-{uuid.uuid4().hex[:6]}",
                timestamp=datetime.now(timezone.utc),
                agent="verification",
                status="failed",
                message=f"Post-remediation verification failed. Escalating incident to human Tier-2. Ref: {tkt_res.get('ticket_id')}"
            )
            await self._emit_event(incident, verify_event)

orchestrator = AgentOrchestrator()
