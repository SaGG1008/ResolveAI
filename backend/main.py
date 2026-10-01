from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import json
import os
import asyncio

from agents import IncidentOrchestrator
from tools import ToolRegistry, RiskPolicy, RiskLevel
from sse import sse_manager, SSEEventType
from approval_gate import approval_gate
from audit_trail import audit_trail

app = FastAPI(title="ResolveAI API", version="1.0.0")

# Initialize components
orchestrator = IncidentOrchestrator()
tool_registry = ToolRegistry()
risk_policy = RiskPolicy()

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# Data Models
# ============================================================================

class Evidence(BaseModel):
    id: str
    type: str  # 'knowledge_base', 'ticket', 'system_status', 'procedure'
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
    riskLevel: str  # 'low', 'medium', 'high', 'critical'
    requiresApproval: bool
    linkedEvidence: list[Evidence]
    reasoning: str

class AgentEvent(BaseModel):
    id: str
    timestamp: datetime
    agent: str  # 'triage', 'investigation', 'diagnosis', 'action_planner', 'verification'
    status: str  # 'started', 'processing', 'completed', 'failed'
    message: str
    evidence: Optional[list[Evidence]] = None
    diagnosis: Optional[Diagnosis] = None
    action: Optional[Action] = None

class Resolution(BaseModel):
    timestamp: datetime
    verificationMethod: str
    success: bool

class Incident(BaseModel):
    id: str
    title: str
    description: str
    status: str  # 'open', 'investigating', 'diagnosed', 'pending_approval', 'executing', 'verifying', 'resolved', 'escalated'
    createdAt: datetime
    updatedAt: datetime
    priority: str  # 'low', 'medium', 'high', 'critical'
    category: str
    events: list[AgentEvent]
    evidence: list[Evidence]
    diagnosis: Optional[Diagnosis] = None
    proposedAction: Optional[Action] = None
    approvalRequired: bool
    escalationReason: Optional[str] = None
    resolution: Optional[Resolution] = None

class NewIncidentRequest(BaseModel):
    title: str
    description: str
    category: str

class DashboardMetrics(BaseModel):
    activeIncidents: int
    aiResolutions: int
    escalations: int
    avgResolutionTime: int

# ============================================================================
# In-Memory Storage (will be replaced with database in full implementation)
# ============================================================================

incidents_db: dict[str, dict] = {}
next_incident_id = 1

def load_mock_data():
    """Load mock incidents for demo"""
    global incidents_db, next_incident_id

    # VPN incident
    incidents_db['INC-001'] = {
        "id": "INC-001",
        "title": "Cannot connect to VPN",
        "description": "User unable to authenticate to corporate VPN. Getting \"invalid token\" error.",
        "status": "resolved",
        "createdAt": datetime.now(),
        "updatedAt": datetime.now(),
        "priority": "high",
        "category": "VPN",
        "events": [],
        "evidence": [],
        "approvalRequired": False,
        "resolution": {
            "timestamp": datetime.now(),
            "verificationMethod": "User login verification",
            "success": True
        }
    }

    # Email incident
    incidents_db['INC-002'] = {
        "id": "INC-002",
        "title": "Email sync errors on Outlook",
        "description": "Employee reports Outlook not syncing email. Messages are delayed by 2+ hours.",
        "status": "resolved",
        "createdAt": datetime.now(),
        "updatedAt": datetime.now(),
        "priority": "medium",
        "category": "Email",
        "events": [],
        "evidence": [],
        "approvalRequired": False,
        "resolution": {
            "timestamp": datetime.now(),
            "verificationMethod": "Manual sync test",
            "success": True
        }
    }

    # Security incident
    incidents_db['INC-003'] = {
        "id": "INC-003",
        "title": "Suspicious login attempts detected",
        "description": "Security team detected multiple failed login attempts from unusual location.",
        "status": "escalated",
        "createdAt": datetime.now(),
        "updatedAt": datetime.now(),
        "priority": "critical",
        "category": "Security",
        "events": [],
        "evidence": [],
        "approvalRequired": True,
        "escalationReason": "High-risk security incident requires human judgment and approval before action."
    }

    next_incident_id = 4

load_mock_data()

# ============================================================================
# API Endpoints
# ============================================================================

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ResolveAI API",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/api/dashboard-metrics")
@app.get("/api/dashboard/metrics")
async def get_dashboard_metrics():
    """Get dashboard KPI metrics"""
    active = sum(1 for i in incidents_db.values() if i["status"] in ["open", "investigating", "diagnosed", "pending_approval", "executing", "verifying"])
    resolved = sum(1 for i in incidents_db.values() if i["status"] == "resolved")
    escalated = sum(1 for i in incidents_db.values() if i["status"] == "escalated")

    return DashboardMetrics(
        activeIncidents=active,
        aiResolutions=resolved,
        escalations=escalated,
        avgResolutionTime=8
    )

@app.get("/api/incidents")
async def list_incidents():
    """Get all incidents"""
    incidents = list(incidents_db.values())
    # Sort by creation date, most recent first
    incidents.sort(key=lambda x: x.get('createdAt', datetime.now()), reverse=True)
    return incidents

@app.get("/api/incidents/{incident_id}")
async def get_incident(incident_id: str):
    """Get a specific incident by ID"""
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")
    return incidents_db[incident_id]

@app.post("/api/incidents")
async def create_incident(request: NewIncidentRequest):
    """Create a new incident"""
    global next_incident_id

    incident_id = f"INC-{next_incident_id:03d}"
    next_incident_id += 1

    now = datetime.now()
    new_incident = {
        "id": incident_id,
        "title": request.title,
        "description": request.description,
        "status": "open",
        "createdAt": now,
        "updatedAt": now,
        "priority": "medium",
        "category": request.category,
        "events": [],
        "evidence": [],
        "approvalRequired": False
    }

    incidents_db[incident_id] = new_incident
    return new_incident

@app.post("/api/incidents/{incident_id}/approve")
async def approve_incident_action(incident_id: str, approved: bool = True, operator_id: str = "admin", operator_notes: str = None):
    """Approve or reject an action for an incident"""
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

    incident = incidents_db[incident_id]

    # Get pending approval request
    approval_request = approval_gate.get_pending_request(incident_id)
    if not approval_request:
        raise HTTPException(status_code=400, detail="No pending approval for this incident")

    if approved:
        # Approve the action
        approval_gate.approve(incident_id, operator_id, operator_notes)
        audit_trail.log_approval_granted(incident_id, operator_id, approval_request.tool_name, operator_notes)

        # Emit event
        sse_manager.emit_trace_event(incident_id, "system", f"Action approved by {operator_id}", "completed")
        sse_manager.emit_state_changed(incident_id, incident["status"], "executing", "Action approved, executing")

        # Execute the tool
        incident["status"] = "executing"
        tool_result = tool_registry.execute_tool(approval_request.tool_name, user_id=incident.get("user_id", "unknown"))

        # Emit tool execution event
        sse_manager.emit_tool_executed(
            incident_id,
            approval_request.tool_name,
            tool_result.success,
            tool_result.message,
            tool_result.data
        )
        audit_trail.log_tool_executed(incident_id, approval_request.tool_name, tool_result.success, tool_result.message, tool_result.data)

        if tool_result.success:
            # Verification
            incident["status"] = "verifying"
            sse_manager.emit_state_changed(incident_id, "executing", "verifying", "Verifying resolution")
            audit_trail.log_state_transition(incident_id, "executing", "verifying", "Tool execution succeeded")

            # Run verification tool with issue_type and action_taken
            verify_result = tool_registry.execute_tool(
                "verify_resolution",
                issue_type=incident["category"],
                action_taken=approval_request.tool_name
            )

            if verify_result.success:
                incident["status"] = "resolved"
                incident["resolution"] = {
                    "timestamp": datetime.now().isoformat(),
                    "verificationMethod": "Automated verification",
                    "success": True
                }
                sse_manager.emit_resolution_verified(incident_id, True, "automated", "Resolution verified successfully")
                audit_trail.log_verification_result(incident_id, True, "automated", "Resolution verified")
                audit_trail.log_incident_resolved(incident_id, "tool_execution")
                sse_manager.emit_state_changed(incident_id, "verifying", "resolved", "Resolution verified")
            else:
                incident["status"] = "escalated"
                incident["escalationReason"] = "Verification failed"
                sse_manager.emit_resolution_verified(incident_id, False, "automated", "Verification failed")
                audit_trail.log_verification_result(incident_id, False, "automated", "Verification failed")
                audit_trail.log_incident_escalated(incident_id, "Verification failed")
                sse_manager.emit_state_changed(incident_id, "verifying", "escalated", "Verification failed")
        else:
            incident["status"] = "escalated"
            incident["escalationReason"] = f"Tool execution failed: {tool_result.message}"
            sse_manager.emit_state_changed(incident_id, "executing", "escalated", f"Tool failed: {tool_result.message}")
            audit_trail.log_incident_escalated(incident_id, f"Tool execution failed: {tool_result.message}")
    else:
        # Reject the action
        rejection_reason = operator_notes or "Operator declined"
        approval_gate.reject(incident_id, operator_id, rejection_reason)
        audit_trail.log_approval_rejected(incident_id, operator_id, approval_request.tool_name, rejection_reason)

        # Emit event
        sse_manager.emit_trace_event(incident_id, "system", f"Action rejected by {operator_id}: {rejection_reason}", "completed")
        sse_manager.emit_state_changed(incident_id, incident["status"], "escalated", f"Approval rejected: {rejection_reason}")

        incident["status"] = "escalated"
        incident["escalationReason"] = rejection_reason
        audit_trail.log_incident_escalated(incident_id, f"Approval rejected: {rejection_reason}")

    incident["updatedAt"] = datetime.now()
    incident["approvalRequired"] = False
    return incident

@app.post("/api/incidents/{incident_id}/escalate")
async def escalate_incident(incident_id: str, reason: str = "Requires human review"):
    """Escalate an incident"""
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

    incident = incidents_db[incident_id]
    old_status = incident["status"]
    incident["status"] = "escalated"
    incident["escalationReason"] = reason
    incident["updatedAt"] = datetime.now()

    # Emit SSE event
    sse_manager.emit_state_changed(incident_id, old_status, "escalated", reason)
    audit_trail.log_incident_escalated(incident_id, reason)

    return incident


@app.get("/api/incidents/{incident_id}/stream")
async def stream_incident_events(incident_id: str):
    """
    Server-Sent Events stream for real-time incident lifecycle updates.

    Emits events as the incident progresses through agents and approval gates:
    - trace_event: Agent processing steps
    - evidence_discovered: New evidence found
    - state_changed: Incident state transitions
    - action_required: Approval gate triggered
    - tool_executed: Tool execution result
    - resolution_verified: Verification complete
    """
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

    # Subscribe to events
    sse_manager.subscribe(incident_id)
    sse_manager.create_queue(incident_id)

    async def event_generator():
        """Generate SSE events for the incident lifecycle."""
        last_index = 0

        try:
            while True:
                # Get new events since last check
                events = sse_manager.get_events(incident_id)

                if len(events) > last_index:
                    # Stream new events
                    for event in events[last_index:]:
                        yield event.to_sse_format()
                    last_index = len(events)

                # Check if incident is in terminal state
                incident = incidents_db.get(incident_id)
                if incident and incident["status"] in ["resolved", "escalated"]:
                    # Send final state update
                    yield f"event: incident_terminal\ndata: {json.dumps({'status': incident['status']})}\n\n"
                    break

                # Wait before checking again (reduces CPU usage)
                await asyncio.sleep(0.5)

        finally:
            # Unsubscribe from events
            sse_manager.unsubscribe(incident_id)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        }
    )

@app.post("/api/incidents/{incident_id}/resolve")
async def resolve_incident(incident_id: str, verification_method: str = "Automated verification"):
    """Mark an incident as resolved"""
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

    incident = incidents_db[incident_id]
    incident["status"] = "resolved"
    incident["resolution"] = {
        "timestamp": datetime.now().isoformat(),
        "verificationMethod": verification_method,
        "success": True
    }
    incident["updatedAt"] = datetime.now()

    return incident

@app.post("/api/incidents/{incident_id}/analyze")
async def analyze_incident(incident_id: str):
    """Analyze an incident using the AI agent pipeline"""
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

    incident = incidents_db[incident_id]

    # Initialize SSE event queue for this incident
    sse_manager.create_queue(incident_id)
    audit_trail.log_state_transition(incident_id, incident["status"], "investigating", "Analysis started")

    # Emit event: investigation started
    sse_manager.emit_trace_event(incident_id, "system", "Starting incident analysis pipeline", "started")
    sse_manager.emit_state_changed(incident_id, incident["status"], "investigating", "Analysis pipeline initiated")

    # Update incident status
    old_status = incident["status"]
    incident["status"] = "investigating"
    incident["updatedAt"] = datetime.now()

    # Run the agent pipeline
    result = orchestrator.process_incident(incident["title"], incident["description"])

    # Emit evidence collection events
    if result["evidence"]:
        sse_manager.emit_trace_event(incident_id, "investigation_agent", f"Collected {len(result['evidence'])} evidence items", "completed")
        audit_trail.log_evidence_collected(incident_id, len(result["evidence"]), [e.source for e in result["evidence"]])

    # Emit diagnosis event
    if result["diagnosis"]:
        sse_manager.emit_trace_event(incident_id, "diagnosis_agent", f"Root cause: {result['diagnosis'].likelyCause}", "completed")
        audit_trail.log_diagnosis_generated(incident_id, result["diagnosis"].likelyCause, result["diagnosis"].confidence)

    # Emit action planning event
    if result["action"]:
        sse_manager.emit_trace_event(incident_id, "action_planner_agent", f"Selected tool: {result['action'].tool}", "completed")
        audit_trail.log_action_proposed(incident_id, result["action"].tool, result["action"].riskLevel, result["action"].requiresApproval)

        # Check if approval is required
        if result["action"].requiresApproval or result["action"].riskLevel in ["high", "critical"]:
            # Create approval request
            approval_request = approval_gate.create_approval_request(
                incident_id,
                result["action"].tool,
                result["action"].riskLevel,
                result["action"].description,
                result["action"].reasoning,
                [e.dict() for e in result["action"].linkedEvidence]
            )

            # Emit approval required event
            sse_manager.emit_action_required(
                incident_id,
                "approval_required",
                result["action"].tool,
                result["action"].riskLevel,
                f"Tool execution requires human approval"
            )

            # Update incident status
            incident["status"] = "pending_approval"
            incident["proposedAction"] = result["action"].dict()
            audit_trail.log_approval_requested(incident_id, approval_request.id, result["action"].tool)
            audit_trail.log_state_transition(incident_id, "investigating", "pending_approval", "High-risk tool requires approval")
            sse_manager.emit_state_changed(incident_id, "investigating", "pending_approval", "High-risk tool requires approval")
        else:
            # Low-risk tool, can execute
            incident["status"] = "executing"
            incident["proposedAction"] = result["action"].dict()
            audit_trail.log_state_transition(incident_id, "investigating", "executing", "Executing low-risk tool")
            sse_manager.emit_state_changed(incident_id, "investigating", "executing", "Executing low-risk tool")

            # Execute the tool
            tool_result = tool_registry.execute_tool(result["action"].tool, user_id=incident.get("user_id", "unknown"))

            # Emit tool execution event
            sse_manager.emit_tool_executed(
                incident_id,
                result["action"].tool,
                tool_result.success,
                tool_result.message,
                tool_result.data
            )
            audit_trail.log_tool_executed(incident_id, result["action"].tool, tool_result.success, tool_result.message, tool_result.data)

            if tool_result.success:
                # Verification
                incident["status"] = "verifying"
                sse_manager.emit_state_changed(incident_id, "executing", "verifying", "Verifying resolution")
                audit_trail.log_state_transition(incident_id, "executing", "verifying", "Tool execution succeeded")

                # Run verification tool with issue_type and action_taken
                verify_result = tool_registry.execute_tool(
                    "verify_resolution",
                    issue_type=incident["category"],
                    action_taken=result["action"].tool
                )

                if verify_result.success:
                    incident["status"] = "resolved"
                    incident["resolution"] = {
                        "timestamp": datetime.now().isoformat(),
                        "verificationMethod": "Automated verification",
                        "success": True
                    }
                    sse_manager.emit_resolution_verified(incident_id, True, "automated", "Resolution verified successfully")
                    audit_trail.log_verification_result(incident_id, True, "automated", "Resolution verified")
                    audit_trail.log_incident_resolved(incident_id, "tool_execution")
                    sse_manager.emit_state_changed(incident_id, "verifying", "resolved", "Resolution verified")
                else:
                    incident["status"] = "escalated"
                    incident["escalationReason"] = "Verification failed"
                    sse_manager.emit_resolution_verified(incident_id, False, "automated", "Verification failed")
                    audit_trail.log_verification_result(incident_id, False, "automated", "Verification failed")
                    audit_trail.log_incident_escalated(incident_id, "Verification failed")
                    sse_manager.emit_state_changed(incident_id, "verifying", "escalated", "Verification failed")
            else:
                incident["status"] = "escalated"
                incident["escalationReason"] = f"Tool execution failed: {tool_result.message}"
                sse_manager.emit_state_changed(incident_id, "executing", "escalated", f"Tool failed: {tool_result.message}")
                audit_trail.log_incident_escalated(incident_id, f"Tool execution failed: {tool_result.message}")
    else:
        # No suitable action found
        incident["status"] = "escalated"
        incident["escalationReason"] = "No suitable automated action found"
        sse_manager.emit_state_changed(incident_id, "investigating", "escalated", "No automated action available")
        audit_trail.log_incident_escalated(incident_id, "No suitable automated action found")

    # Update incident with analysis results
    incident["events"] = [e.dict() for e in result["events"]]
    incident["evidence"] = [e.dict() for e in result["evidence"]]
    incident["diagnosis"] = result["diagnosis"].dict() if result["diagnosis"] else None
    incident["approvalRequired"] = approval_gate.get_pending_request(incident_id) is not None
    incident["updatedAt"] = datetime.now()

    return incident

@app.get("/api/tools")
async def list_tools():
    """List all available tools in the registry."""
    return tool_registry.list_tools()

@app.get("/api/tools/by-category")
async def get_tools_by_category():
    """Get tools organized by category."""
    return tool_registry.get_tools_by_category()

@app.get("/api/incidents/{incident_id}/audit-trail")
async def get_incident_audit_trail(incident_id: str):
    """Get complete audit trail for an incident."""
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

    return {
        "incident_id": incident_id,
        "audit_trail": audit_trail.get_trail_json(incident_id),
        "summary": audit_trail.get_summary(incident_id),
    }

@app.get("/api/incidents/{incident_id}/approval-status")
async def get_approval_status(incident_id: str):
    """Get approval status for an incident."""
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

    return approval_gate.get_summary(incident_id)

from pydantic import BaseModel
from typing import Dict, Any


class ExecuteToolRequest(BaseModel):
    """Request body for tool execution."""
    name: str
    parameters: Dict[str, Any] = {}


@app.post("/api/tools/execute")
async def execute_tool(request: ExecuteToolRequest):
    """
    Execute a tool with validated inputs.

    Request body:
    - name: Tool name to execute
    - parameters: Tool-specific parameters

    Returns:
        Standardized ToolResult
    """
    try:
        result = tool_registry.execute_tool(request.name, **request.parameters)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tool execution failed: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "service": "ResolveAI API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health",
            "metrics": "/api/dashboard-metrics",
            "incidents": {
                "list": "GET /api/incidents",
                "create": "POST /api/incidents",
                "analyze": "POST /api/incidents/{incident_id}/analyze",
                "get": "GET /api/incidents/{incident_id}",
                "approve": "POST /api/incidents/{incident_id}/approve",
                "escalate": "POST /api/incidents/{incident_id}/escalate",
                "resolve": "POST /api/incidents/{incident_id}/resolve"
            }
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
