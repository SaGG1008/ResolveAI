"""
ResolveAI Agent Orchestration System

Implements a 5-agent pipeline for incident resolution:
1. Triage Agent - Classify and prioritize issues
2. Investigation Agent - Gather evidence
3. Diagnosis Agent - Determine root cause
4. Action Planner - Select remediation action
5. Verification Agent - Verify resolution success
"""

from enum import Enum
from datetime import datetime
from typing import Optional, Any
from pydantic import BaseModel
import json
import uuid

# ============================================================================
# Agent Types and Enums
# ============================================================================

class AgentType(str, Enum):
    TRIAGE = "triage"
    INVESTIGATION = "investigation"
    DIAGNOSIS = "diagnosis"
    ACTION_PLANNER = "action_planner"
    VERIFICATION = "verification"

class EventStatus(str, Enum):
    STARTED = "started"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# ============================================================================
# Data Models
# ============================================================================

class Evidence(BaseModel):
    id: str
    type: str
    title: str
    content: str
    relevance: int
    source: Optional[str] = None

class Diagnosis(BaseModel):
    likelyCause: str
    confidence: int
    supportingEvidence: list[Evidence]
    uncertainty: Optional[str] = None

class Action(BaseModel):
    id: str
    tool: str
    description: str
    riskLevel: RiskLevel
    requiresApproval: bool
    linkedEvidence: list[Evidence]
    reasoning: str

class AgentEvent(BaseModel):
    id: str
    timestamp: datetime
    agent: AgentType
    status: EventStatus
    message: str
    evidence: Optional[list[Evidence]] = None
    diagnosis: Optional[Diagnosis] = None
    action: Optional[Action] = None

# ============================================================================
# Knowledge Bases (Mock Data)
# ============================================================================

KNOWLEDGE_BASE = [
    {
        "id": "kb_vpn",
        "type": "knowledge_base",
        "title": "VPN Token Expiration Issues",
        "content": "When VPN tokens expire, users cannot authenticate. Common solution: request new token or use token reset procedure.",
        "keywords": ["vpn", "token", "authentication", "cannot connect"],
        "relevance": 95,
    },
    {
        "id": "kb_email",
        "type": "knowledge_base",
        "title": "Outlook Sync Issues",
        "content": "Outlook sync delays are often caused by cache corruption or Exchange sync issues. Solution: Clear Outlook cache and restart.",
        "keywords": ["email", "outlook", "sync", "delay"],
        "relevance": 90,
    },
    {
        "id": "kb_security",
        "type": "knowledge_base",
        "title": "Suspicious Login Detection",
        "content": "Multiple failed login attempts from unusual locations indicate potential security breach. Action: Reset credentials and enable MFA.",
        "keywords": ["security", "login", "suspicious", "breach"],
        "relevance": 100,
    },
]

PREVIOUS_TICKETS = [
    {
        "id": "tkt_vpn_001",
        "type": "ticket",
        "title": "Similar VPN Issue - User john.doe",
        "content": "User reported identical symptoms. Resolved by VPN token reset on 2026-09-28.",
        "keywords": ["vpn", "token", "reset"],
        "relevance": 88,
    },
    {
        "id": "tkt_email_001",
        "type": "ticket",
        "title": "Outlook Cache Issues",
        "content": "Multiple users reported sync delays. Fixed by clearing Exchange cache.",
        "keywords": ["email", "outlook", "cache"],
        "relevance": 85,
    },
]

PROCEDURES = [
    {
        "id": "proc_vpn_reset",
        "type": "procedure",
        "title": "VPN Token Reset Procedure",
        "content": "1. Navigate to VPN admin console. 2. Find user account. 3. Click 'Reset Token'. 4. User receives new token via email. 5. Verify login works.",
        "keywords": ["vpn", "token", "reset"],
        "tools": ["reset_vpn_token"],
    },
    {
        "id": "proc_email_cache",
        "type": "procedure",
        "title": "Clear Outlook Cache",
        "content": "1. Close Outlook. 2. Navigate to AppData\\Local\\Microsoft\\Outlook. 3. Delete .ost files. 4. Restart Outlook. 5. Re-sync mailbox.",
        "keywords": ["email", "outlook", "cache", "sync"],
        "tools": ["clear_outlook_cache"],
    },
]

SYSTEM_STATUS = {
    "vpn_auth": "OPERATIONAL",
    "email_exchange": "OPERATIONAL",
    "security_monitoring": "OPERATIONAL",
}

# ============================================================================
# Agent Classes
# ============================================================================

class Agent:
    """Base agent class"""

    def __init__(self, agent_type: AgentType):
        self.type = agent_type

    def create_event(self, message: str, status: EventStatus, **kwargs) -> AgentEvent:
        """Create an agent event"""
        return AgentEvent(
            id=str(uuid.uuid4()),
            timestamp=datetime.now(),
            agent=self.type,
            status=status,
            message=message,
            **kwargs
        )

class TriageAgent(Agent):
    """Classifies and prioritizes issues"""

    def __init__(self):
        super().__init__(AgentType.TRIAGE)

    def process(self, title: str, description: str) -> AgentEvent:
        """Triage an incident"""
        # Simple heuristic-based classification
        combined_text = (title + " " + description).lower()

        if "vpn" in combined_text:
            category = "VPN"
            priority = "high"
        elif "email" in combined_text or "outlook" in combined_text:
            category = "Email"
            priority = "medium"
        elif "security" in combined_text or "suspicious" in combined_text or "login" in combined_text:
            category = "Security"
            priority = "critical"
        else:
            category = "General"
            priority = "medium"

        return self.create_event(
            f"Issue classified as {category}. Priority: {priority.upper()}.",
            EventStatus.COMPLETED,
            metadata={"category": category, "priority": priority}
        )

class InvestigationAgent(Agent):
    """Gathers evidence from multiple sources"""

    def __init__(self):
        super().__init__(AgentType.INVESTIGATION)

    def process(self, title: str, description: str, category: str) -> AgentEvent:
        """Investigate an incident"""
        combined_text = (title + " " + description).lower()
        evidence = []

        # Search knowledge base
        for kb in KNOWLEDGE_BASE:
            for keyword in kb.get("keywords", []):
                if keyword in combined_text:
                    evidence.append(Evidence(
                        id=kb["id"],
                        type=kb["type"],
                        title=kb["title"],
                        content=kb["content"],
                        relevance=kb["relevance"],
                        source="Knowledge Base",
                    ))
                    break

        # Search previous tickets
        for ticket in PREVIOUS_TICKETS:
            for keyword in ticket.get("keywords", []):
                if keyword in combined_text:
                    evidence.append(Evidence(
                        id=ticket["id"],
                        type=ticket["type"],
                        title=ticket["title"],
                        content=ticket["content"],
                        relevance=ticket["relevance"],
                        source="Ticket History",
                    ))
                    break

        # Get procedures
        for proc in PROCEDURES:
            for keyword in proc.get("keywords", []):
                if keyword in combined_text:
                    evidence.append(Evidence(
                        id=proc["id"],
                        type=proc["type"],
                        title=proc["title"],
                        content=proc["content"],
                        relevance=95,
                        source="IT Procedures",
                    ))
                    break

        return self.create_event(
            f"Investigation complete. Found {len(evidence)} relevant evidence items.",
            EventStatus.COMPLETED,
            evidence=evidence
        )

class DiagnosisAgent(Agent):
    """Determines root cause from evidence"""

    def __init__(self):
        super().__init__(AgentType.DIAGNOSIS)

    def process(self, title: str, description: str, evidence: list[Evidence]) -> AgentEvent:
        """Diagnose an incident"""
        combined_text = (title + " " + description).lower()

        # Determine likely cause based on evidence and text
        if "vpn" in combined_text and evidence:
            likely_cause = "User VPN token has expired and requires renewal"
            confidence = 96
            uncertainty = "Small chance of network connectivity issue, but evidence strongly suggests token expiration."
        elif "email" in combined_text or "outlook" in combined_text:
            likely_cause = "Exchange cache corruption or sync lag"
            confidence = 88
            uncertainty = "Could also be mailbox quota issue, but cache corruption is most likely."
        elif "security" in combined_text or "suspicious" in combined_text:
            likely_cause = "Potential security breach - unusual login pattern detected"
            confidence = 92
            uncertainty = None
        else:
            likely_cause = "Unable to determine cause from available evidence"
            confidence = 45
            uncertainty = "Requires additional investigation or human review."

        # Use top evidence items as supporting
        supporting_evidence = evidence[:2] if evidence else []

        diagnosis = Diagnosis(
            likelyCause=likely_cause,
            confidence=confidence,
            supportingEvidence=supporting_evidence,
            uncertainty=uncertainty,
        )

        return self.create_event(
            f"Root cause identified: {likely_cause}",
            EventStatus.COMPLETED,
            diagnosis=diagnosis
        )

class ActionPlannerAgent(Agent):
    """Selects appropriate remediation action"""

    def __init__(self):
        super().__init__(AgentType.ACTION_PLANNER)

    def process(self, title: str, description: str, category: str, evidence: list[Evidence]) -> Optional[AgentEvent]:
        """Plan an action"""
        combined_text = (title + " " + description).lower()

        action = None

        # VPN scenarios
        if "vpn" in combined_text and ("token" in combined_text or "authentication" in combined_text):
            action = Action(
                id=str(uuid.uuid4()),
                tool="reset_vpn_token",
                description="Reset user VPN token and send new credentials via email",
                riskLevel=RiskLevel.LOW,
                requiresApproval=False,
                linkedEvidence=evidence[:2],
                reasoning="Low-risk operation supported by KB article and successful precedent ticket.",
            )
        elif "email" in combined_text or "outlook" in combined_text:
            action = Action(
                id=str(uuid.uuid4()),
                tool="clear_outlook_cache",
                description="Clear Outlook cache and restart Exchange sync",
                riskLevel=RiskLevel.LOW,
                requiresApproval=False,
                linkedEvidence=evidence[:2],
                reasoning="Standard cache-clearing procedure with no risk of data loss.",
            )
        elif "security" in combined_text or "suspicious" in combined_text:
            # Security issues require escalation, not auto-action
            return self.create_event(
                "Action: ESCALATE to Security team for manual investigation.",
                EventStatus.COMPLETED,
                action=None
            )

        if action:
            return self.create_event(
                f"Selected action: {action.tool}",
                EventStatus.COMPLETED,
                action=action
            )
        else:
            return self.create_event(
                "No suitable automated action found. Escalating to human review.",
                EventStatus.COMPLETED,
                action=None
            )

class VerificationAgent(Agent):
    """Verifies resolution success"""

    def __init__(self):
        super().__init__(AgentType.VERIFICATION)

    def process(self, title: str, description: str, action_executed: bool = False) -> AgentEvent:
        """Verify resolution"""
        if action_executed:
            combined_text = (title + " " + description).lower()

            if "vpn" in combined_text:
                message = "Verification: User successfully authenticated to VPN. Issue RESOLVED."
                success = True
            elif "email" in combined_text:
                message = "Verification: Outlook sync restored. Email delivery normal. Issue RESOLVED."
                success = True
            else:
                message = "Verification: Action executed. Awaiting confirmation of resolution."
                success = True

            return self.create_event(message, EventStatus.COMPLETED)
        else:
            return self.create_event(
                "Action not executed. Awaiting manual verification or human intervention.",
                EventStatus.COMPLETED
            )

# ============================================================================
# Orchestrator
# ============================================================================

class IncidentOrchestrator:
    """Orchestrates the 5-agent pipeline"""

    def __init__(self):
        self.triage_agent = TriageAgent()
        self.investigation_agent = InvestigationAgent()
        self.diagnosis_agent = DiagnosisAgent()
        self.action_planner_agent = ActionPlannerAgent()
        self.verification_agent = VerificationAgent()

    def process_incident(self, title: str, description: str) -> dict[str, Any]:
        """Process an incident through the full pipeline"""
        events = []
        evidence = []
        diagnosis = None
        action = None
        requires_escalation = False

        # Stage 1: Triage
        triage_event = self.triage_agent.process(title, description)
        events.append(triage_event)
        category = triage_event.dict().get("metadata", {}).get("category", "General")

        # Stage 2: Investigation
        investigation_event = self.investigation_agent.process(title, description, category)
        events.append(investigation_event)
        evidence = investigation_event.evidence or []

        # Stage 3: Diagnosis
        diagnosis_event = self.diagnosis_agent.process(title, description, evidence)
        events.append(diagnosis_event)
        diagnosis = diagnosis_event.diagnosis

        # Stage 4: Action Planning
        action_event = self.action_planner_agent.process(title, description, category, evidence)
        events.append(action_event)
        action = action_event.action

        # Check if escalation is needed
        if "ESCALATE" in action_event.message or not action:
            requires_escalation = True

        # Stage 5: Verification (if action was selected)
        if action and not requires_escalation:
            verification_event = self.verification_agent.process(title, description, action_executed=True)
        else:
            verification_event = self.verification_agent.process(title, description, action_executed=False)
        events.append(verification_event)

        return {
            "events": events,
            "evidence": evidence,
            "diagnosis": diagnosis,
            "action": action,
            "requires_escalation": requires_escalation,
            "final_status": "escalated" if requires_escalation else ("verifying" if action else "pending_approval"),
        }
