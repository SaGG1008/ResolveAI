"""
Audit Trail System for ResolveAI.

Records all significant events in the incident resolution pipeline:
- Incident creation and state transitions
- Agent processing steps
- Tool execution and results
- Approval decisions
- Verification outcomes

Provides complete audit log for compliance and debugging.
"""

from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from enum import Enum
import uuid


class AuditEventType(str, Enum):
    INCIDENT_CREATED = "incident_created"
    STATE_TRANSITION = "state_transition"
    AGENT_STARTED = "agent_started"
    AGENT_COMPLETED = "agent_completed"
    EVIDENCE_COLLECTED = "evidence_collected"
    DIAGNOSIS_GENERATED = "diagnosis_generated"
    ACTION_PROPOSED = "action_proposed"
    APPROVAL_REQUESTED = "approval_requested"
    APPROVAL_GRANTED = "approval_granted"
    APPROVAL_REJECTED = "approval_rejected"
    TOOL_EXECUTED = "tool_executed"
    TOOL_FAILED = "tool_failed"
    VERIFICATION_PASSED = "verification_passed"
    VERIFICATION_FAILED = "verification_failed"
    INCIDENT_RESOLVED = "incident_resolved"
    INCIDENT_ESCALATED = "incident_escalated"
    ERROR_OCCURRED = "error_occurred"


@dataclass
class AuditEntry:
    """Single entry in the audit trail."""

    id: str
    timestamp: str
    incident_id: str
    event_type: AuditEventType
    actor: str  # 'system', 'agent_name', 'operator_id'
    action: str  # Human-readable description
    details: Dict[str, Any]
    severity: str  # 'info', 'warning', 'error'

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "incident_id": self.incident_id,
            "event_type": self.event_type.value,
            "actor": self.actor,
            "action": self.action,
            "details": self.details,
            "severity": self.severity,
        }


class AuditTrail:
    """
    Maintains complete audit trail for all incidents.

    In MVP: in-memory storage
    In production: persistent database (PostgreSQL, MongoDB, etc.)
    """

    def __init__(self):
        # All audit entries across all incidents
        # Key: incident_id, Value: list of AuditEntry
        self.entries: Dict[str, List[AuditEntry]] = {}
        # Total entry count for ID generation
        self.entry_count = 0

    def _ensure_incident_log(self, incident_id: str) -> None:
        """Ensure incident has an audit log."""
        if incident_id not in self.entries:
            self.entries[incident_id] = []

    def log(
        self,
        incident_id: str,
        event_type: AuditEventType,
        actor: str,
        action: str,
        details: Dict[str, Any] = None,
        severity: str = "info",
    ) -> AuditEntry:
        """
        Log an audit entry.

        Args:
            incident_id: Target incident
            event_type: Type of event
            actor: Who/what triggered event (system, agent, operator)
            action: Human-readable action description
            details: Event-specific details
            severity: 'info', 'warning', 'error'

        Returns:
            The created AuditEntry
        """
        self._ensure_incident_log(incident_id)

        entry = AuditEntry(
            id=f"audit_{self.entry_count:06d}",
            timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
            incident_id=incident_id,
            event_type=event_type,
            actor=actor,
            action=action,
            details=details or {},
            severity=severity,
        )

        self.entry_count += 1
        self.entries[incident_id].append(entry)

        return entry

    def log_incident_created(
        self,
        incident_id: str,
        title: str,
        category: str,
    ) -> AuditEntry:
        """Log incident creation."""
        return self.log(
            incident_id,
            AuditEventType.INCIDENT_CREATED,
            "system",
            f"Incident created: {title}",
            details={"title": title, "category": category},
        )

    def log_state_transition(
        self,
        incident_id: str,
        old_state: str,
        new_state: str,
        reason: str = None,
    ) -> AuditEntry:
        """Log incident state transition."""
        return self.log(
            incident_id,
            AuditEventType.STATE_TRANSITION,
            "system",
            f"State: {old_state} → {new_state}",
            details={"old_state": old_state, "new_state": new_state, "reason": reason},
        )

    def log_agent_started(
        self,
        incident_id: str,
        agent_name: str,
    ) -> AuditEntry:
        """Log agent processing start."""
        return self.log(
            incident_id,
            AuditEventType.AGENT_STARTED,
            agent_name,
            f"{agent_name} started processing",
            details={"agent": agent_name},
        )

    def log_agent_completed(
        self,
        incident_id: str,
        agent_name: str,
        result: str,
    ) -> AuditEntry:
        """Log agent completion."""
        return self.log(
            incident_id,
            AuditEventType.AGENT_COMPLETED,
            agent_name,
            f"{agent_name} completed: {result}",
            details={"agent": agent_name, "result": result},
        )

    def log_evidence_collected(
        self,
        incident_id: str,
        evidence_count: int,
        sources: List[str],
    ) -> AuditEntry:
        """Log evidence collection."""
        return self.log(
            incident_id,
            AuditEventType.EVIDENCE_COLLECTED,
            "system",
            f"Collected {evidence_count} evidence items from {', '.join(sources)}",
            details={"evidence_count": evidence_count, "sources": sources},
        )

    def log_diagnosis_generated(
        self,
        incident_id: str,
        root_cause: str,
        confidence: int,
    ) -> AuditEntry:
        """Log diagnosis generation."""
        return self.log(
            incident_id,
            AuditEventType.DIAGNOSIS_GENERATED,
            "system",
            f"Diagnosis: {root_cause} (confidence: {confidence}%)",
            details={"root_cause": root_cause, "confidence": confidence},
        )

    def log_action_proposed(
        self,
        incident_id: str,
        tool_name: str,
        risk_level: str,
        requires_approval: bool,
    ) -> AuditEntry:
        """Log proposed action."""
        return self.log(
            incident_id,
            AuditEventType.ACTION_PROPOSED,
            "system",
            f"Action proposed: {tool_name} ({risk_level} risk)",
            details={"tool": tool_name, "risk_level": risk_level, "requires_approval": requires_approval},
        )

    def log_approval_requested(
        self,
        incident_id: str,
        approval_id: str,
        tool_name: str,
    ) -> AuditEntry:
        """Log approval request creation."""
        return self.log(
            incident_id,
            AuditEventType.APPROVAL_REQUESTED,
            "system",
            f"Approval requested for {tool_name}",
            details={"approval_id": approval_id, "tool": tool_name},
            severity="warning",
        )

    def log_approval_granted(
        self,
        incident_id: str,
        operator_id: str,
        tool_name: str,
        notes: str = None,
    ) -> AuditEntry:
        """Log approval grant."""
        return self.log(
            incident_id,
            AuditEventType.APPROVAL_GRANTED,
            operator_id,
            f"Approved execution of {tool_name}",
            details={"tool": tool_name, "operator_notes": notes},
        )

    def log_approval_rejected(
        self,
        incident_id: str,
        operator_id: str,
        tool_name: str,
        reason: str,
    ) -> AuditEntry:
        """Log approval rejection."""
        return self.log(
            incident_id,
            AuditEventType.APPROVAL_REJECTED,
            operator_id,
            f"Rejected execution of {tool_name}: {reason}",
            details={"tool": tool_name, "reason": reason},
            severity="warning",
        )

    def log_tool_executed(
        self,
        incident_id: str,
        tool_name: str,
        success: bool,
        message: str,
        data: Dict[str, Any] = None,
    ) -> AuditEntry:
        """Log tool execution."""
        event_type = AuditEventType.TOOL_EXECUTED if success else AuditEventType.TOOL_FAILED
        severity = "info" if success else "error"

        return self.log(
            incident_id,
            event_type,
            "system",
            f"Tool {tool_name}: {message}",
            details={"tool": tool_name, "success": success, "data": data},
            severity=severity,
        )

    def log_verification_result(
        self,
        incident_id: str,
        success: bool,
        method: str,
        message: str,
    ) -> AuditEntry:
        """Log verification outcome."""
        event_type = AuditEventType.VERIFICATION_PASSED if success else AuditEventType.VERIFICATION_FAILED

        return self.log(
            incident_id,
            event_type,
            "system",
            f"Verification {('passed' if success else 'failed')}: {message}",
            details={"method": method, "success": success},
        )

    def log_incident_resolved(
        self,
        incident_id: str,
        resolution_method: str,
    ) -> AuditEntry:
        """Log incident resolution."""
        return self.log(
            incident_id,
            AuditEventType.INCIDENT_RESOLVED,
            "system",
            f"Incident resolved via {resolution_method}",
            details={"resolution_method": resolution_method},
        )

    def log_incident_escalated(
        self,
        incident_id: str,
        reason: str,
    ) -> AuditEntry:
        """Log incident escalation."""
        return self.log(
            incident_id,
            AuditEventType.INCIDENT_ESCALATED,
            "system",
            f"Escalated to human review: {reason}",
            details={"reason": reason},
            severity="warning",
        )

    def log_error(
        self,
        incident_id: str,
        error_code: str,
        error_message: str,
    ) -> AuditEntry:
        """Log error event."""
        return self.log(
            incident_id,
            AuditEventType.ERROR_OCCURRED,
            "system",
            f"Error: {error_message}",
            details={"error_code": error_code, "error_message": error_message},
            severity="error",
        )

    def get_trail(self, incident_id: str) -> List[AuditEntry]:
        """Get complete audit trail for an incident."""
        self._ensure_incident_log(incident_id)
        return self.entries[incident_id]

    def get_trail_json(self, incident_id: str) -> List[Dict[str, Any]]:
        """Get audit trail as JSON-serializable list."""
        return [entry.to_dict() for entry in self.get_trail(incident_id)]

    def get_summary(self, incident_id: str) -> Dict[str, Any]:
        """Get audit summary for an incident."""
        trail = self.get_trail(incident_id)

        event_counts = {}
        for entry in trail:
            event_type = entry.event_type.value
            event_counts[event_type] = event_counts.get(event_type, 0) + 1

        errors = [e for e in trail if e.severity == "error"]
        warnings = [e for e in trail if e.severity == "warning"]

        return {
            "incident_id": incident_id,
            "total_events": len(trail),
            "event_types": event_counts,
            "error_count": len(errors),
            "warning_count": len(warnings),
            "first_event": trail[0].timestamp if trail else None,
            "last_event": trail[-1].timestamp if trail else None,
        }


# Global audit trail instance
audit_trail = AuditTrail()
