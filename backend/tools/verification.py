"""
Verification tools for ResolveAI.
"""

from .base import Tool, ToolInputSchema, ToolResult, RiskLevel


class VerifyResolutionToolInput(ToolInputSchema):
    """Input schema for verify_resolution tool."""
    issue_type: str
    action_taken: str


class VerifyResolutionTool(Tool):
    """
    Verify that an issue has been successfully resolved.

    Risk Level: LOW
    Approval Required: No

    Simulates verifying that a remediation action resolved the issue.
    """

    name = "verify_resolution"
    description = "Verify that an issue has been successfully resolved"
    input_schema = VerifyResolutionToolInput
    risk_level = RiskLevel.LOW
    approval_required = False
    allows_self_verification = True

    def __init__(self, simulated_state: dict = None):
        super().__init__(simulated_state)

        if "verifications" not in self.simulated_state:
            self.simulated_state["verifications"] = []

    def execute(self, issue_type: str, action_taken: str) -> ToolResult:
        """
        Verify that an issue has been resolved.

        Args:
            issue_type: Type of issue that was addressed
            action_taken: Action that was performed

        Returns:
            ToolResult with verification status
        """
        # Simulate verification logic based on issue type and action
        verification_id = f"VER-{len(self.simulated_state.get('verifications', [])) + 1:04d}"

        # For VPN issues with token reset, verification typically passes
        vpn_scenarios = ["vpn", "authentication", "token"]
        email_scenarios = ["email", "outlook", "sync"]

        is_vpn_issue = any(s in issue_type.lower() for s in vpn_scenarios)
        is_email_issue = any(s in issue_type.lower() for s in email_scenarios)

        # Check if the action matches the issue type
        action_matches_issue = False
        if is_vpn_issue and "vpn" in action_taken.lower() and "token" in action_taken.lower():
            action_matches_issue = True
        elif is_email_issue and "cache" in action_taken.lower():
            action_matches_issue = True
        elif "service" in action_taken.lower() and "restart" in action_taken.lower():
            action_matches_issue = True

        # Simulate verification result
        if is_vpn_issue and action_matches_issue:
            verification_result = True
            message = "Verification successful: VPN authentication restored"
        elif is_email_issue and action_matches_issue:
            verification_result = True
            message = "Verification successful: Email sync restored"
        else:
            # Random verification result (simulating real-world uncertainty)
            verification_result = True  # For demo, assume success
            message = "Verification successful: Issue appears resolved"

        verification = {
            "id": verification_id,
            "issue_type": issue_type,
            "action_taken": action_taken,
            "verified": verification_result,
            "timestamp": "2026-10-01T10:30:00Z",
        }

        self.simulated_state["verifications"].append(verification)

        return ToolResult(
            success=True,
            tool=self.name,
            status="success",
            message=message,
            data={
                "verification_id": verification_id,
                "verified": verification_result,
                "verification": verification,
            },
        )
