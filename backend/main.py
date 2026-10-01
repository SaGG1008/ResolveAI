from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import json
import os

from agents import IncidentOrchestrator

app = FastAPI(title="ResolveAI API", version="1.0.0")

# Initialize orchestrator
orchestrator = IncidentOrchestrator()

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
async def approve_incident_action(incident_id: str):
    """Approve an action for an incident"""
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

    incident = incidents_db[incident_id]
    incident["status"] = "executing"
    incident["updatedAt"] = datetime.now()

    return incident

@app.post("/api/incidents/{incident_id}/escalate")
async def escalate_incident(incident_id: str, reason: str = "Requires human review"):
    """Escalate an incident"""
    if incident_id not in incidents_db:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found")

    incident = incidents_db[incident_id]
    incident["status"] = "escalated"
    incident["escalationReason"] = reason
    incident["updatedAt"] = datetime.now()

    return incident

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

    # Run the agent pipeline
    result = orchestrator.process_incident(incident["title"], incident["description"])

    # Update incident with analysis results
    incident["events"] = [e.dict() for e in result["events"]]
    incident["evidence"] = [e.dict() for e in result["evidence"]]
    incident["diagnosis"] = result["diagnosis"].dict() if result["diagnosis"] else None
    incident["proposedAction"] = result["action"].dict() if result["action"] else None
    incident["approvalRequired"] = result["action"].requiresApproval if result["action"] else False
    incident["status"] = result["final_status"]
    incident["escalationReason"] = "High-risk incident requires human approval." if result["requires_escalation"] else None
    incident["updatedAt"] = datetime.now()

    return incident

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
