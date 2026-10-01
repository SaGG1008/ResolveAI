"""
Phase 5 Integration Tests: SSE Real-Time Verification & Approval Gates

Tests for:
1. SSE event emission during incident lifecycle
2. Approval gate enforcement for HIGH/CRITICAL tools
3. State transitions with audit trail
4. Tool execution from orchestrator
5. Verification agent determining SUCCESS/FAILURE
6. Complete end-to-end incident resolution flow
7. Failure scenarios (tool failures, rejected approvals)
"""

import pytest
import asyncio
from datetime import datetime

from tools import ToolRegistry, RiskLevel
from sse import sse_manager, SSEEventType
from approval_gate import approval_gate, ApprovalStatus
from audit_trail import audit_trail, AuditEventType


class TestSSEEventEmission:
    """Test SSE event emission during incident lifecycle."""

    def test_sse_queue_creation(self):
        """Test that SSE queue is created for incident."""
        incident_id = "INC-TEST-001"
        sse_manager.create_queue(incident_id)

        assert incident_id in sse_manager.event_queues
        assert len(sse_manager.get_events(incident_id)) == 0

    def test_emit_trace_event(self):
        """Test emitting a trace event."""
        incident_id = "INC-TEST-002"
        sse_manager.create_queue(incident_id)

        sse_manager.emit_trace_event(
            incident_id,
            "triage_agent",
            "Classifying issue as VPN",
            "completed"
        )

        events = sse_manager.get_events(incident_id)
        assert len(events) == 1
        assert events[0].event_type == SSEEventType.TRACE_EVENT
        assert "triage_agent" in events[0].to_sse_format()

    def test_emit_evidence_discovered(self):
        """Test emitting evidence discovery event."""
        incident_id = "INC-TEST-003"
        sse_manager.create_queue(incident_id)

        sse_manager.emit_evidence_discovered(
            incident_id,
            "ev_001",
            "KNOWLEDGE_BASE",
            "VPN Token Issues",
            "Token expiration causes authentication failures",
            0.95
        )

        events = sse_manager.get_events(incident_id)
        assert len(events) == 1
        assert events[0].event_type == SSEEventType.EVIDENCE_DISCOVERED

    def test_emit_state_changed(self):
        """Test emitting state change event."""
        incident_id = "INC-TEST-004"
        sse_manager.create_queue(incident_id)

        sse_manager.emit_state_changed(
            incident_id,
            "open",
            "investigating",
            "Analysis started"
        )

        events = sse_manager.get_events(incident_id)
        assert len(events) == 1
        assert events[0].event_type == SSEEventType.STATE_CHANGED
        assert "open" in events[0].to_sse_format()
        assert "investigating" in events[0].to_sse_format()

    def test_emit_action_required(self):
        """Test emitting approval gate trigger event."""
        incident_id = "INC-TEST-005"
        sse_manager.create_queue(incident_id)

        sse_manager.emit_action_required(
            incident_id,
            "approval_required",
            "restart_service",
            "high",
            "Service restart requires human approval"
        )

        events = sse_manager.get_events(incident_id)
        assert len(events) == 1
        assert events[0].event_type == SSEEventType.ACTION_REQUIRED
        assert "restart_service" in events[0].to_sse_format()

    def test_emit_tool_executed(self):
        """Test emitting tool execution event."""
        incident_id = "INC-TEST-006"
        sse_manager.create_queue(incident_id)

        sse_manager.emit_tool_executed(
            incident_id,
            "reset_vpn_token",
            True,
            "VPN token reset successfully",
            {"token_hash": "HASH_12345"}
        )

        events = sse_manager.get_events(incident_id)
        assert len(events) == 1
        assert events[0].event_type == SSEEventType.TOOL_EXECUTED
        assert events[0].data["success"] == True

    def test_emit_resolution_verified(self):
        """Test emitting verification result event."""
        incident_id = "INC-TEST-007"
        sse_manager.create_queue(incident_id)

        sse_manager.emit_resolution_verified(
            incident_id,
            True,
            "automated_probe",
            "User successfully authenticated to VPN"
        )

        events = sse_manager.get_events(incident_id)
        assert len(events) == 1
        assert events[0].event_type == SSEEventType.RESOLUTION_VERIFIED
        assert events[0].data["resolved"] == True

    def test_sse_event_format(self):
        """Test SSE wire format is correct."""
        incident_id = "INC-TEST-008"
        sse_manager.create_queue(incident_id)

        sse_manager.emit_state_changed(incident_id, "open", "investigating")

        events = sse_manager.get_events(incident_id)
        formatted = events[0].to_sse_format()

        # Should have event type line, data line, and blank line
        assert "event: state_changed" in formatted
        assert "data: " in formatted
        assert formatted.endswith("\n\n")


class TestApprovalGateEnforcement:
    """Test approval gate enforcement."""

    def test_low_risk_no_approval(self):
        """Test LOW risk tools don't require approval."""
        assert not approval_gate.check_requires_approval("reset_vpn_token", "low")

    def test_medium_risk_no_approval(self):
        """Test MEDIUM risk tools don't require approval."""
        assert not approval_gate.check_requires_approval("restart_service", "medium")

    def test_high_risk_requires_approval(self):
        """Test HIGH risk tools require approval."""
        assert approval_gate.check_requires_approval("escalate_to_human", "high")

    def test_critical_risk_requires_approval(self):
        """Test CRITICAL risk tools require approval."""
        assert approval_gate.check_requires_approval("dangerous_tool", "critical")

    def test_create_approval_request(self):
        """Test creating an approval request."""
        incident_id = "INC-APPR-001"

        request = approval_gate.create_approval_request(
            incident_id,
            "restart_service",
            "high",
            "Restart email service",
            "Email service is degraded and needs restart",
            [{"id": "ev_001", "title": "Service down"}]
        )

        assert request.incident_id == incident_id
        assert request.tool_name == "restart_service"
        assert request.status == ApprovalStatus.PENDING
        assert approval_gate.get_pending_request(incident_id) == request

    def test_approve_request(self):
        """Test approving an approval request."""
        incident_id = "INC-APPR-002"

        approval_gate.create_approval_request(
            incident_id,
            "restart_service",
            "high",
            "Restart service",
            "Service needs restart"
        )

        assert approval_gate.approve(incident_id, "operator_123", "Approved for maintenance window")
        assert approval_gate.get_pending_request(incident_id) is None

        # Check history
        history = approval_gate.get_approval_history(incident_id)
        assert len(history) == 1
        assert history[0].status == ApprovalStatus.APPROVED
        assert history[0].operator_id == "operator_123"

    def test_reject_request(self):
        """Test rejecting an approval request."""
        incident_id = "INC-APPR-003"

        approval_gate.create_approval_request(
            incident_id,
            "restart_service",
            "high",
            "Restart service",
            "Service needs restart"
        )

        assert approval_gate.reject(incident_id, "operator_456", "Too risky during business hours")
        assert approval_gate.get_pending_request(incident_id) is None

        # Check history
        history = approval_gate.get_approval_history(incident_id)
        assert len(history) == 1
        assert history[0].status == ApprovalStatus.REJECTED
        assert "Too risky" in history[0].operator_notes

    def test_approval_summary(self):
        """Test approval status summary."""
        incident_id = "INC-APPR-004"

        approval_gate.create_approval_request(
            incident_id,
            "restart_service",
            "high",
            "Restart service",
            "Needs restart"
        )

        summary = approval_gate.get_summary(incident_id)
        assert summary["status"] == "pending_approval"
        assert summary["pending_request"]["tool_name"] == "restart_service"
        assert summary["pending_request"]["risk_level"] == "high"


class TestAuditTrailLogging:
    """Test audit trail logging."""

    def test_log_incident_created(self):
        """Test logging incident creation."""
        incident_id = "INC-AUDIT-001"

        audit_trail.log_incident_created(incident_id, "Cannot connect to VPN", "VPN")

        trail = audit_trail.get_trail(incident_id)
        assert len(trail) == 1
        assert trail[0].event_type == AuditEventType.INCIDENT_CREATED
        assert "Cannot connect to VPN" in trail[0].details["title"]

    def test_log_state_transition(self):
        """Test logging state transitions."""
        incident_id = "INC-AUDIT-002"

        audit_trail.log_state_transition(incident_id, "open", "investigating", "Analysis started")

        trail = audit_trail.get_trail(incident_id)
        assert len(trail) == 1
        assert trail[0].event_type == AuditEventType.STATE_TRANSITION
        assert trail[0].details["old_state"] == "open"
        assert trail[0].details["new_state"] == "investigating"

    def test_log_agent_lifecycle(self):
        """Test logging agent start and completion."""
        incident_id = "INC-AUDIT-003"

        audit_trail.log_agent_started(incident_id, "triage_agent")
        audit_trail.log_agent_completed(incident_id, "triage_agent", "Classified as VPN issue")

        trail = audit_trail.get_trail(incident_id)
        assert len(trail) == 2
        assert trail[0].event_type == AuditEventType.AGENT_STARTED
        assert trail[1].event_type == AuditEventType.AGENT_COMPLETED

    def test_log_evidence_collection(self):
        """Test logging evidence collection."""
        incident_id = "INC-AUDIT-004"

        audit_trail.log_evidence_collected(
            incident_id,
            3,
            ["Knowledge Base", "Ticket History", "System Status"]
        )

        trail = audit_trail.get_trail(incident_id)
        assert len(trail) == 1
        assert trail[0].event_type == AuditEventType.EVIDENCE_COLLECTED
        assert trail[0].details["evidence_count"] == 3

    def test_log_tool_execution(self):
        """Test logging tool execution."""
        incident_id = "INC-AUDIT-005"

        audit_trail.log_tool_executed(
            incident_id,
            "reset_vpn_token",
            True,
            "VPN token reset successfully",
            {"user_id": "user_123", "token_reset": True}
        )

        trail = audit_trail.get_trail(incident_id)
        assert len(trail) == 1
        assert trail[0].event_type == AuditEventType.TOOL_EXECUTED
        assert trail[0].details["tool"] == "reset_vpn_token"
        assert trail[0].details["success"] == True

    def test_log_approval_flow(self):
        """Test logging approval flow."""
        incident_id = "INC-AUDIT-006"

        audit_trail.log_approval_requested(incident_id, "appr_001", "restart_service")
        audit_trail.log_approval_granted(incident_id, "operator_789", "restart_service", "Approved")

        trail = audit_trail.get_trail(incident_id)
        assert len(trail) == 2
        assert trail[0].event_type == AuditEventType.APPROVAL_REQUESTED
        assert trail[1].event_type == AuditEventType.APPROVAL_GRANTED

    def test_audit_trail_summary(self):
        """Test audit trail summary generation."""
        incident_id = "INC-AUDIT-007"

        audit_trail.log_incident_created(incident_id, "Test incident", "Test")
        audit_trail.log_state_transition(incident_id, "open", "investigating")
        audit_trail.log_agent_started(incident_id, "triage_agent")
        audit_trail.log_error(incident_id, "TOOL_FAILED", "Tool execution failed")

        summary = audit_trail.get_summary(incident_id)
        assert summary["incident_id"] == incident_id
        assert summary["total_events"] == 4
        assert summary["error_count"] == 1
        assert AuditEventType.STATE_TRANSITION.value in summary["event_types"]


class TestToolExecutionIntegration:
    """Test tool execution from orchestrator."""

    def test_reset_vpn_token_execution(self):
        """Test executing reset_vpn_token tool."""
        registry = ToolRegistry()

        result = registry.execute_tool("reset_vpn_token", user_id="test_user")

        assert result.success
        assert "VPN token reset" in result.message
        assert result.data["user_id"] == "test_user"

    def test_get_system_status_execution(self):
        """Test executing get_system_status tool."""
        registry = ToolRegistry()

        result = registry.execute_tool("get_system_status")

        assert result.success
        assert "services" in result.data
        assert result.data["total_services"] == 4

    def test_verify_resolution_execution(self):
        """Test executing verify_resolution tool."""
        registry = ToolRegistry()

        # verify_resolution requires issue_type and action_taken parameters
        result = registry.execute_tool("verify_resolution", issue_type="VPN authentication", action_taken="VPN token reset")

        assert result.success
        assert "verification" in result.message.lower()  # Message says "verification successful"
        assert "verification_id" in result.data


class TestIncidentLifecycleFlow:
    """Test complete incident lifecycle with SSE and approval gates."""

    def test_vpn_incident_low_risk_flow(self):
        """
        Test complete VPN incident resolution (LOW risk):
        Create → Triage → Investigation → Diagnosis → Action Plan → Execute → Verify → Resolved
        """
        incident_id = "INC-FLOW-001"
        sse_manager.create_queue(incident_id)

        # Simulate incident creation
        audit_trail.log_incident_created(incident_id, "Cannot connect to VPN", "VPN")
        sse_manager.emit_state_changed(incident_id, "open", "investigating")
        audit_trail.log_state_transition(incident_id, "open", "investigating")

        # Simulate investigation
        audit_trail.log_evidence_collected(incident_id, 2, ["KB", "Tickets"])
        sse_manager.emit_evidence_discovered(incident_id, "ev_001", "KB", "VPN Issues", "VPN token", 0.95)

        # Simulate diagnosis
        audit_trail.log_diagnosis_generated(incident_id, "VPN token expired", 96)

        # Simulate action planning (LOW risk, no approval needed)
        audit_trail.log_action_proposed(incident_id, "reset_vpn_token", "low", False)
        sse_manager.emit_state_changed(incident_id, "investigating", "executing")
        audit_trail.log_state_transition(incident_id, "investigating", "executing")

        # Execute tool
        registry = ToolRegistry()
        tool_result = registry.execute_tool("reset_vpn_token", user_id="test_user")
        audit_trail.log_tool_executed(incident_id, "reset_vpn_token", tool_result.success, tool_result.message)
        sse_manager.emit_tool_executed(incident_id, "reset_vpn_token", tool_result.success, tool_result.message)

        # Verify resolution
        sse_manager.emit_state_changed(incident_id, "executing", "verifying")
        verify_result = registry.execute_tool("verify_resolution")
        audit_trail.log_verification_result(incident_id, verify_result.success, "automated", verify_result.message)
        sse_manager.emit_resolution_verified(incident_id, verify_result.success, "automated", verify_result.message)

        # Resolve
        sse_manager.emit_state_changed(incident_id, "verifying", "resolved")
        audit_trail.log_incident_resolved(incident_id, "tool_execution")

        # Verify complete flow
        trail = audit_trail.get_trail(incident_id)
        events = sse_manager.get_events(incident_id)

        assert len(trail) >= 9  # Multiple audit entries (at least 9 for this flow)
        assert len(events) >= 5  # Multiple SSE events

        # Check key transitions are recorded
        event_types = [e.event_type for e in trail]
        assert AuditEventType.INCIDENT_CREATED in event_types
        assert AuditEventType.STATE_TRANSITION in event_types
        assert AuditEventType.TOOL_EXECUTED in event_types
        assert AuditEventType.INCIDENT_RESOLVED in event_types

    def test_approval_gate_blocks_high_risk(self):
        """
        Test approval gate blocks HIGH risk tool execution:
        Create → Plan → Action Requires Approval → Pending Approval → Approve → Execute
        """
        incident_id = "INC-FLOW-002"
        sse_manager.create_queue(incident_id)

        audit_trail.log_incident_created(incident_id, "Service restart needed", "Service")

        # Action planning: HIGH risk tool selected
        audit_trail.log_action_proposed(incident_id, "restart_service", "high", True)

        # Approval gate triggered
        approval_request = approval_gate.create_approval_request(
            incident_id,
            "restart_service",
            "high",
            "Restart email service",
            "Service is degraded"
        )
        audit_trail.log_approval_requested(incident_id, approval_request.id, "restart_service")
        sse_manager.emit_action_required(
            incident_id,
            "approval_required",
            "restart_service",
            "high",
            "Tool requires human approval"
        )

        # Verify pending approval
        assert approval_gate.get_pending_request(incident_id) is not None
        summary = approval_gate.get_summary(incident_id)
        assert summary["status"] == "pending_approval"

        # Operator approves
        approval_gate.approve(incident_id, "operator_001", "Approved for maintenance")
        audit_trail.log_approval_granted(incident_id, "operator_001", "restart_service", "Approved")
        sse_manager.emit_trace_event(incident_id, "system", "Action approved", "completed")

        # Verify approval removed
        assert approval_gate.get_pending_request(incident_id) is None

        # Check audit trail
        trail = audit_trail.get_trail(incident_id)
        event_types = [e.event_type for e in trail]
        assert AuditEventType.APPROVAL_REQUESTED in event_types
        assert AuditEventType.APPROVAL_GRANTED in event_types


class TestFailureScenarios:
    """Test failure scenarios and error handling."""

    def test_tool_execution_failure(self):
        """Test handling of tool execution failure."""
        incident_id = "INC-FAIL-001"

        audit_trail.log_state_transition(incident_id, "investigating", "executing")
        audit_trail.log_tool_executed(incident_id, "reset_vpn_token", False, "User not found")
        audit_trail.log_incident_escalated(incident_id, "Tool execution failed: User not found")

        trail = audit_trail.get_trail(incident_id)
        event_types = [e.event_type for e in trail]

        assert AuditEventType.INCIDENT_ESCALATED in event_types

    def test_approval_rejection(self):
        """Test handling of approval rejection."""
        incident_id = "INC-FAIL-002"

        approval_request = approval_gate.create_approval_request(
            incident_id,
            "restart_service",
            "high",
            "Restart service",
            "Needs restart"
        )

        approval_gate.reject(incident_id, "operator_002", "Too risky during business hours")
        audit_trail.log_approval_rejected(
            incident_id,
            "operator_002",
            "restart_service",
            "Too risky during business hours"
        )
        audit_trail.log_incident_escalated(incident_id, "Approval rejected: Too risky during business hours")

        trail = audit_trail.get_trail(incident_id)
        event_types = [e.event_type for e in trail]

        assert AuditEventType.APPROVAL_REJECTED in event_types
        assert AuditEventType.INCIDENT_ESCALATED in event_types

    def test_verification_failure(self):
        """Test handling of verification failure."""
        incident_id = "INC-FAIL-003"

        audit_trail.log_state_transition(incident_id, "executing", "verifying")
        audit_trail.log_verification_result(incident_id, False, "automated", "User still cannot connect")
        audit_trail.log_incident_escalated(incident_id, "Verification failed")

        trail = audit_trail.get_trail(incident_id)
        event_types = [e.event_type for e in trail]

        assert AuditEventType.VERIFICATION_FAILED in event_types
        assert AuditEventType.INCIDENT_ESCALATED in event_types


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
