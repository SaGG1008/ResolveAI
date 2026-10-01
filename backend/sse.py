"""
Server-Sent Events (SSE) for real-time incident lifecycle streaming.

Manages event emission as incidents progress through the agent pipeline:
- trace_event: Agent processing steps
- evidence_discovered: New evidence found
- state_changed: Incident state transitions
- action_required: Approval gate triggered
- tool_executed: Tool execution result
- resolution_verified: Verification complete
"""

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Optional, Any, Dict, List
from enum import Enum
import json


class SSEEventType(str, Enum):
    TRACE_EVENT = "trace_event"
    EVIDENCE_DISCOVERED = "evidence_discovered"
    STATE_CHANGED = "state_changed"
    ACTION_REQUIRED = "action_required"
    TOOL_EXECUTED = "tool_executed"
    RESOLUTION_VERIFIED = "resolution_verified"
    ERROR = "error"


@dataclass
class SSEEvent:
    """Represents a single SSE event to be streamed to client."""

    event_type: SSEEventType
    incident_id: str
    data: Dict[str, Any]
    timestamp: str = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")

    def to_sse_format(self) -> str:
        """Convert to SSE wire format for streaming."""
        payload = {
            "incident_id": self.incident_id,
            "timestamp": self.timestamp,
            **self.data
        }
        return f"event: {self.event_type.value}\ndata: {json.dumps(payload)}\n\n"


class SSEStreamManager:
    """
    Manages SSE connections and event broadcasting.

    In production, this would integrate with a message queue (Redis, RabbitMQ)
    for multi-instance support. For MVP, uses in-memory queues per incident.
    """

    def __init__(self):
        # In-memory event queues per incident
        # Key: incident_id, Value: list of SSEEvent
        self.event_queues: Dict[str, List[SSEEvent]] = {}
        # Active subscriber counts per incident
        self.subscribers: Dict[str, int] = {}

    def create_queue(self, incident_id: str) -> None:
        """Create event queue for an incident."""
        if incident_id not in self.event_queues:
            self.event_queues[incident_id] = []
            self.subscribers[incident_id] = 0

    def emit_event(self, incident_id: str, event: SSEEvent) -> None:
        """
        Emit an event to an incident's stream.

        Args:
            incident_id: Target incident
            event: Event to emit
        """
        if incident_id not in self.event_queues:
            self.create_queue(incident_id)

        self.event_queues[incident_id].append(event)

    def emit_trace_event(
        self,
        incident_id: str,
        agent: str,
        thought: str,
        status: str,
    ) -> None:
        """Emit a trace event from an agent."""
        event = SSEEvent(
            event_type=SSEEventType.TRACE_EVENT,
            incident_id=incident_id,
            data={
                "agent": agent,
                "thought": thought,
                "status": status,
            }
        )
        self.emit_event(incident_id, event)

    def emit_evidence_discovered(
        self,
        incident_id: str,
        evidence_id: str,
        source_type: str,
        title: str,
        snippet: str,
        relevance_score: float,
    ) -> None:
        """Emit an evidence discovery event."""
        event = SSEEvent(
            event_type=SSEEventType.EVIDENCE_DISCOVERED,
            incident_id=incident_id,
            data={
                "evidence_id": evidence_id,
                "source_type": source_type,
                "title": title,
                "snippet": snippet,
                "relevance_score": relevance_score,
            }
        )
        self.emit_event(incident_id, event)

    def emit_state_changed(
        self,
        incident_id: str,
        old_state: str,
        new_state: str,
        reason: str = None,
    ) -> None:
        """Emit a state change event."""
        event = SSEEvent(
            event_type=SSEEventType.STATE_CHANGED,
            incident_id=incident_id,
            data={
                "old_state": old_state,
                "new_state": new_state,
                "reason": reason or f"Transitioning from {old_state} to {new_state}",
            }
        )
        self.emit_event(incident_id, event)

    def emit_action_required(
        self,
        incident_id: str,
        action_type: str,
        tool_name: str,
        risk_level: str,
        message: str,
    ) -> None:
        """Emit an approval gate trigger event."""
        event = SSEEvent(
            event_type=SSEEventType.ACTION_REQUIRED,
            incident_id=incident_id,
            data={
                "action_type": action_type,  # 'approval_required' or 'escalation'
                "tool_name": tool_name,
                "risk_level": risk_level,
                "message": message,
            }
        )
        self.emit_event(incident_id, event)

    def emit_tool_executed(
        self,
        incident_id: str,
        tool_name: str,
        success: bool,
        message: str,
        data: Optional[Dict] = None,
    ) -> None:
        """Emit a tool execution result event."""
        event = SSEEvent(
            event_type=SSEEventType.TOOL_EXECUTED,
            incident_id=incident_id,
            data={
                "tool_name": tool_name,
                "success": success,
                "message": message,
                "data": data or {},
            }
        )
        self.emit_event(incident_id, event)

    def emit_resolution_verified(
        self,
        incident_id: str,
        resolved: bool,
        method: str,
        message: str,
    ) -> None:
        """Emit a verification result event."""
        event = SSEEvent(
            event_type=SSEEventType.RESOLUTION_VERIFIED,
            incident_id=incident_id,
            data={
                "resolved": resolved,
                "method": method,
                "message": message,
            }
        )
        self.emit_event(incident_id, event)

    def emit_error(
        self,
        incident_id: str,
        error_code: str,
        error_message: str,
        details: Optional[Dict] = None,
    ) -> None:
        """Emit an error event."""
        event = SSEEvent(
            event_type=SSEEventType.ERROR,
            incident_id=incident_id,
            data={
                "error_code": error_code,
                "error_message": error_message,
                "details": details or {},
            }
        )
        self.emit_event(incident_id, event)

    def get_events(self, incident_id: str) -> List[SSEEvent]:
        """Get all events for an incident."""
        if incident_id not in self.event_queues:
            self.create_queue(incident_id)
        return self.event_queues[incident_id]

    def subscribe(self, incident_id: str) -> None:
        """Record a new subscriber."""
        if incident_id not in self.subscribers:
            self.create_queue(incident_id)
        self.subscribers[incident_id] += 1

    def unsubscribe(self, incident_id: str) -> None:
        """Record a subscriber disconnection."""
        if incident_id in self.subscribers:
            self.subscribers[incident_id] = max(0, self.subscribers[incident_id] - 1)

    def clear_queue(self, incident_id: str) -> None:
        """Clear event queue for an incident (after successful streaming)."""
        if incident_id in self.event_queues:
            self.event_queues[incident_id] = []


# Global SSE stream manager instance
sse_manager = SSEStreamManager()
