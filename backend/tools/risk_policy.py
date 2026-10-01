"""
Risk Policy Layer for ResolveAI Tool Registry.

Centralized policy for determining:
- Risk levels for tool selection
- Approval requirements
- Execution guards
- Escalation triggers
"""

from enum import Enum
from typing import Optional
from .base import RiskLevel


class RiskPolicy:
    """
    Centralized risk policy for tool execution.

    Defines the organization's policy for:
    - Auto-execution thresholds
    - Approval requirements
    - Escalation triggers
    - Audit logging requirements
    """

    def __init__(self):
        # Risk thresholds for automatic execution
        self.auto_execute_risk_levels = [RiskLevel.LOW]
        self.moderate_risk_levels = [RiskLevel.MEDIUM]
        self.approval_required_levels = [RiskLevel.HIGH, RiskLevel.CRITICAL, RiskLevel.UNKNOWN]

        # Tool-specific overrides
        self.tool_risk_overrides: dict[str, RiskLevel] = {}
        self.tool_approval_overrides: dict[str, bool] = {}

    def get_risk_level(self, tool_name: str, default: RiskLevel = RiskLevel.UNKNOWN) -> RiskLevel:
        """
        Get the risk level for a tool.

        Args:
            tool_name: Name of the tool
            default: Default risk level if not found

        Returns:
            RiskLevel for the tool
        """
        return self.tool_risk_overrides.get(tool_name, default)

    def requires_approval(self, tool_name: str, risk_level: Optional[RiskLevel] = None) -> bool:
        """
        Check if a tool requires human approval.

        Args:
            tool_name: Name of the tool
            risk_level: Optional explicit risk level

        Returns:
            True if approval is required
        """
        # Use explicit risk level if provided
        if risk_level is not None:
            return risk_level in self.approval_required_levels

        # Check tool-specific override
        if tool_name in self.tool_approval_overrides:
            return self.tool_approval_overrides[tool_name]

        # Otherwise check the tool's registered risk level
        if tool_name in self.tool_risk_overrides:
            return self.tool_risk_overrides[tool_name] in self.approval_required_levels

        return False

    def can_auto_execute(self, risk_level: RiskLevel) -> bool:
        """
        Check if a risk level allows auto-execution.

        Args:
            risk_level: Risk level to check

        Returns:
            True if auto-execution is allowed
        """
        return risk_level in self.auto_execute_risk_levels

    def should_escalate(self, risk_level: RiskLevel) -> bool:
        """
        Check if a risk level requires escalation.

        Args:
            risk_level: Risk level to check

        Returns:
            True if escalation is required
        """
        return risk_level in self.approval_required_levels

    def get_audit_required(self, risk_level: RiskLevel) -> bool:
        """
        Check if this risk level requires full audit logging.

        Args:
            risk_level: Risk level to check

        Returns:
            True if audit logging is required
        """
        return risk_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]

    def add_tool_override(self, tool_name: str, risk_level: RiskLevel, approval_required: bool = False) -> None:
        """
        Add a tool-specific risk override.

        Args:
            tool_name: Name of the tool
            risk_level: Risk level for this tool
            approval_required: Whether approval is required
        """
        self.tool_risk_overrides[tool_name] = risk_level
        self.tool_approval_overrides[tool_name] = approval_required

    def get_all_risk_factors(self) -> dict[str, list[str]]:
        """
        Get all risk factors for all registered tools.

        Returns:
            Dict mapping tool names to their risk factors
        """
        return {
            "reset_vpn_token": ["Network service modification", "User authentication change"],
            "restart_service": ["Service interruption possible", "User impact"],
            "clear_dns_cache": ["Network configuration change"],
            "create_ticket": ["Escalation event", "Human workflow trigger"],
            "escalate_to_human": ["Human review required", "Escalation path"],
            "verify_resolution": ["Status verification", "Resolution confirmation"],
        }


# Global risk policy instance
risk_policy = RiskPolicy()

# Register tool-specific overrides
risk_policy.add_tool_override("reset_vpn_token", RiskLevel.LOW, approval_required=False)
risk_policy.add_tool_override("restart_service", RiskLevel.MEDIUM, approval_required=False)
risk_policy.add_tool_override("clear_dns_cache", RiskLevel.LOW, approval_required=False)
risk_policy.add_tool_override("create_ticket", RiskLevel.MEDIUM, approval_required=False)
risk_policy.add_tool_override("escalate_to_human", RiskLevel.HIGH, approval_required=True)
risk_policy.add_tool_override("verify_resolution", RiskLevel.LOW, approval_required=False)
