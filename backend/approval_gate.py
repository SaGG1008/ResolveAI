"""
Approval Gate Enforcement for ResolveAI.

Implements the approval mechanism for high-risk tool execution:
- Blocks execution of HIGH/CRITICAL risk tools
- Requires explicit human approval before proceeding
- Tracks approval decisions in audit trail
- Enforces risk-based escalation
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional, Dict, Any
from enum import Enum
import uuid


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


@dataclass
class ApprovalRequest:
    """Represents a pending approval request."""

    id: str
    incident_id: str
    tool_name: str
    risk_level: str
    action_description: str
    reason: str
    evidence_summary: list
    created_at: str
    status: ApprovalStatus = ApprovalStatus.PENDING
    operator_id: Optional[str] = None
    operator_notes: Optional[str] = None
    approved_at: Optional[str] = None

    def is_expired(self, timeout_seconds: int = 3600) -> bool:
        """Check if approval request has expired."""
        created = datetime.fromisoformat(self.created_at.replace("Z", "+00:00"))
        elapsed = (datetime.utcnow() - created.replace(tzinfo=None)).total_seconds()
        return elapsed > timeout_seconds


class ApprovalGate:
    """
    Enforces approval gates in the incident resolution pipeline.

    Policy:
    - LOW risk: Auto-execute (no approval needed)
    - MEDIUM risk: Monitor (no approval, but audit logged)
    - HIGH risk: Approval required
    - CRITICAL risk: Approval required + escalation
    """

    def __init__(self):
        # Pending approval requests: incident_id -> ApprovalRequest
        self.pending_requests: Dict[str, ApprovalRequest] = {}
        # Approval history for audit trail
        self.approval_history: list[ApprovalRequest] = []

    def check_requires_approval(self, tool_name: str, risk_level: str) -> bool:
        """
        Check if a tool execution requires approval.

        Args:
            tool_name: Name of tool to execute
            risk_level: Risk level (low/medium/high/critical)

        Returns:
            True if approval is required before execution
        """
        return risk_level in ["high", "critical"]

    def create_approval_request(
        self,
        incident_id: str,
        tool_name: str,
        risk_level: str,
        action_description: str,
        reason: str,
        evidence_summary: list = None,
    ) -> ApprovalRequest:
        """
        Create a new approval request for high-risk tool execution.

        Args:
            incident_id: Incident requiring approval
            tool_name: Tool to execute
            risk_level: Risk level assessment
            action_description: Human-readable action description
            reason: Why this action is proposed
            evidence_summary: Supporting evidence items

        Returns:
            ApprovalRequest ready for human review
        """
        request = ApprovalRequest(
            id=str(uuid.uuid4()),
            incident_id=incident_id,
            tool_name=tool_name,
            risk_level=risk_level,
            action_description=action_description,
            reason=reason,
            evidence_summary=evidence_summary or [],
            created_at=datetime.utcnow().isoformat() + "Z",
        )

        # Store in pending requests
        self.pending_requests[incident_id] = request
        return request

    def get_pending_request(self, incident_id: str) -> Optional[ApprovalRequest]:
        """Get pending approval request for an incident."""
        return self.pending_requests.get(incident_id)

    def approve(
        self,
        incident_id: str,
        operator_id: str,
        operator_notes: str = None,
    ) -> bool:
        """
        Approve a pending request.

        Args:
            incident_id: Incident to approve
            operator_id: ID of approving operator
            operator_notes: Optional approval notes

        Returns:
            True if approval succeeded
        """
        request = self.pending_requests.get(incident_id)
        if not request:
            return False

        # Update request
        request.status = ApprovalStatus.APPROVED
        request.operator_id = operator_id
        request.operator_notes = operator_notes
        request.approved_at = datetime.utcnow().isoformat() + "Z"

        # Move to history
        self.approval_history.append(request)
        del self.pending_requests[incident_id]

        return True

    def reject(
        self,
        incident_id: str,
        operator_id: str,
        rejection_reason: str,
    ) -> bool:
        """
        Reject a pending request.

        Args:
            incident_id: Incident to reject
            operator_id: ID of rejecting operator
            rejection_reason: Why the request was rejected

        Returns:
            True if rejection succeeded
        """
        request = self.pending_requests.get(incident_id)
        if not request:
            return False

        # Update request
        request.status = ApprovalStatus.REJECTED
        request.operator_id = operator_id
        request.operator_notes = f"REJECTED: {rejection_reason}"
        request.approved_at = datetime.utcnow().isoformat() + "Z"

        # Move to history
        self.approval_history.append(request)
        del self.pending_requests[incident_id]

        return True

    def get_approval_history(self, incident_id: str = None) -> list[ApprovalRequest]:
        """
        Get approval history.

        Args:
            incident_id: Optional filter by incident

        Returns:
            List of approval requests from history
        """
        if incident_id:
            return [r for r in self.approval_history if r.incident_id == incident_id]
        return self.approval_history

    def get_summary(self, incident_id: str) -> Dict[str, Any]:
        """Get approval status summary for an incident."""
        pending = self.get_pending_request(incident_id)
        history = self.get_approval_history(incident_id)

        if pending:
            return {
                "status": "pending_approval",
                "pending_request": {
                    "id": pending.id,
                    "tool_name": pending.tool_name,
                    "risk_level": pending.risk_level,
                    "action_description": pending.action_description,
                    "reason": pending.reason,
                    "created_at": pending.created_at,
                    "evidence_count": len(pending.evidence_summary),
                },
                "previous_approvals": len([h for h in history if h.status == ApprovalStatus.APPROVED]),
                "previous_rejections": len([h for h in history if h.status == ApprovalStatus.REJECTED]),
            }

        return {
            "status": "no_pending_approval",
            "previous_approvals": len([h for h in history if h.status == ApprovalStatus.APPROVED]),
            "previous_rejections": len([h for h in history if h.status == ApprovalStatus.REJECTED]),
        }


# Global approval gate instance
approval_gate = ApprovalGate()
