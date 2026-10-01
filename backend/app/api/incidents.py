import json
import uuid
import asyncio
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks, status
from fastapi.responses import StreamingResponse
from ..models.schemas import (
    Incident,
    IncidentCreateRequest,
    ApprovalRequest,
    AgentEvent
)
from ..core.db import db
from ..agents.orchestrator import orchestrator

router = APIRouter(prefix="/incidents", tags=["incidents"])

@router.get("", response_model=List[Incident])
async def list_incidents():
    """Retrieve all incidents sorted by creation date."""
    return db.get_all_incidents()

@router.post("", response_model=Incident, status_code=status.HTTP_201_CREATED)
async def create_incident(req: IncidentCreateRequest, background_tasks: BackgroundTasks):
    """Create a new incident and dispatch the multi-agent investigation pipeline."""
    inc_id = f"INC-{uuid.uuid4().hex[:4].upper()}"
    now = datetime.now(timezone.utc)
    
    incident = Incident(
        id=inc_id,
        title=req.title or "New Incident",
        description=req.description,
        status="open",
        createdAt=now,
        updatedAt=now,
        priority=req.priority or "medium",
        category=req.category or "General IT",
        events=[],
        evidence=[]
    )
    
    db.save_incident(incident)

    # Launch multi-agent investigation asynchronously
    background_tasks.add_task(orchestrator.run_investigation_pipeline, inc_id)

    return incident

@router.get("/{incident_id}", response_model=Incident)
async def get_incident(incident_id: str):
    """Retrieve a single incident with all events and evidence."""
    incident = db.get_incident_by_id(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found.")
    return incident

@router.post("/{incident_id}/investigate", response_model=Incident)
async def trigger_investigation(incident_id: str, background_tasks: BackgroundTasks):
    """Trigger or resume agent investigation on an existing incident."""
    incident = db.get_incident_by_id(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found.")
    
    background_tasks.add_task(orchestrator.run_investigation_pipeline, incident_id)
    return incident

@router.post("/{incident_id}/approval", response_model=Incident)
async def handle_approval(incident_id: str, req: ApprovalRequest, background_tasks: BackgroundTasks):
    """Approve or reject a proposed action when incident is pending approval."""
    incident = db.get_incident_by_id(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found.")

    if incident.status != "pending_approval":
        raise HTTPException(status_code=400, detail=f"Incident is in '{incident.status}' state, not 'pending_approval'.")

    if req.approved:
        approval_event = AgentEvent(
            id=f"evt-{uuid.uuid4().hex[:6]}",
            timestamp=datetime.now(timezone.utc),
            agent="action_planner",
            status="completed",
            message=f"Operator '{req.operator_id}' APPROVED the action. Executing remediation and dispatching verification probes...",
            action=incident.proposedAction
        )
        incident.events.append(approval_event)
        incident.approvalRequired = False
        db.save_incident(incident)

        background_tasks.add_task(orchestrator.execute_and_verify, incident)
    else:
        incident.status = "escalated"
        incident.approvalRequired = False
        incident.escalationReason = f"Action rejected by operator ({req.notes or 'No notes provided'}). Escalated to Tier-2 IT Support."
        reject_event = AgentEvent(
            id=f"evt-{uuid.uuid4().hex[:6]}",
            timestamp=datetime.now(timezone.utc),
            agent="action_planner",
            status="failed",
            message=f"Action REJECTED by operator. {incident.escalationReason}"
        )
        incident.events.append(reject_event)
        db.save_incident(incident)

    return incident

@router.get("/{incident_id}/stream")
async def stream_incident_events(incident_id: str):
    """Server-Sent Events (SSE) stream delivering real-time incident state updates."""
    incident = db.get_incident_by_id(incident_id)
    if not incident:
        raise HTTPException(status_code=404, detail=f"Incident {incident_id} not found.")

    async def event_generator():
        queue = orchestrator.subscribe(incident_id)
        try:
            # Send initial state
            yield f"data: {json.dumps(incident.model_dump(mode='json'))}\n\n"
            
            while True:
                try:
                    updated_data = await asyncio.wait_for(queue.get(), timeout=15.0)
                    yield f"data: {json.dumps(updated_data)}\n\n"
                except asyncio.TimeoutError:
                    yield ": keepalive\n\n"
        finally:
            orchestrator.unsubscribe(incident_id, queue)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
    )
