"""
Remediation tools for ResolveAI.
"""

from .base import Tool, ToolInputSchema, ToolResult, RiskLevel


class ResetVpnTokenToolInput(ToolInputSchema):
    """Input schema for reset_vpn_token tool."""
    user_id: str
    reason: str = "User reporting VPN authentication failure"


class ResetVpnTokenTool(Tool):
    """
    Reset user VPN token for authentication issues.

    Risk Level: LOW
    Approval Required: No

    Simulates resetting a VPN token. Updates simulated state with token reset.
    """

    name = "reset_vpn_token"
    description = "Reset user VPN token to resolve authentication issues"
    input_schema = ResetVpnTokenToolInput
    risk_level = RiskLevel.LOW
    approval_required = False

    def __init__(self, simulated_state: dict = None):
        super().__init__(simulated_state)

        # Initialize simulated user state
        if "users" not in self.simulated_state:
            self.simulated_state["users"] = {}

        if "vpn_tokens" not in self.simulated_state:
            self.simulated_state["vpn_tokens"] = {}

    def execute(self, user_id: str, reason: str = "User reporting VPN authentication failure") -> ToolResult:
        """
        Reset VPN token for a user.

        Args:
            user_id: User identifier
            reason: Reason for token reset

        Returns:
            ToolResult with reset confirmation
        """
        # Simulate token reset
        self.simulated_state["vpn_tokens"][user_id] = {
            "token": f"NEW_TOKEN_{user_id}_{self.simulated_state.get('_counter', 0)}",
            "expires_at": "2026-10-02T10:00:00Z",
            "status": "active",
            "reset_reason": reason,
            "reset_by": "system",
        }

        # Update user state
        if user_id not in self.simulated_state["users"]:
            self.simulated_state["users"][user_id] = {}
        self.simulated_state["users"][user_id]["vpn_status"] = "authenticated"

        return ToolResult(
            success=True,
            tool=self.name,
            status="success",
            message=f"VPN token reset successfully for user '{user_id}'",
            data={
                "user_id": user_id,
                "token_reset": True,
                "new_token_hash": f"TOKEN_HASH_{user_id}",
            },
        )


class RestartServiceToolInput(ToolInputSchema):
    """Input schema for restart_service tool."""
    service_name: str
    force: bool = False


class RestartServiceTool(Tool):
    """
    Restart a service to resolve operational issues.

    Risk Level: MEDIUM
    Approval Required: No (medium risk, not high/critical)

    Simulates restarting a service with appropriate state updates.
    """

    name = "restart_service"
    description = "Restart a service to resolve operational issues"
    input_schema = RestartServiceToolInput
    risk_level = RiskLevel.MEDIUM
    approval_required = False

    def __init__(self, simulated_state: dict = None):
        super().__init__(simulated_state)

        if "services" not in self.simulated_state:
            self.simulated_state["services"] = {}

    def execute(self, service_name: str, force: bool = False) -> ToolResult:
        """
        Restart a service.

        Args:
            service_name: Name of the service to restart
            force: Whether to force restart (skip checks)

        Returns:
            ToolResult with restart confirmation
        """
        service_lower = service_name.lower()

        # Simulate service restart
        service_keys = [k for k in self.simulated_state.get("services", {}).keys() if service_lower in k.lower()]

        if not service_keys and service_lower in ["vpn", "vpn_auth"]:
            # Create VPN service if not exists
            self.simulated_state["services"]["vpn_auth"] = {
                "name": "VPN Authentication",
                "status": "restarting",
                "restart_count": self.simulated_state["services"].get("vpn_auth", {}).get("restart_count", 0) + 1,
                "last_restart": "2026-10-01T10:30:00Z",
            }
            # Update to operational after restart
            self.simulated_state["services"]["vpn_auth"]["status"] = "operational"
            service_keys = ["vpn_auth"]

        if service_keys:
            service_key = service_keys[0]
            service = self.simulated_state["services"][service_key]
            service["status"] = "restarting"
            service["restart_count"] = service.get("restart_count", 0) + 1
            service["last_restart"] = "2026-10-01T10:30:00Z"
            service["status"] = "operational"

            return ToolResult(
                success=True,
                tool=self.name,
                status="success",
                message=f"Service '{service.get('name', service_key)}' restarted successfully",
                data={
                    "service": service_key,
                    "service_name": service.get("name", service_key),
                    "restart_count": service["restart_count"],
                },
            )
        else:
            return ToolResult(
                success=False,
                tool=self.name,
                status="failure",
                message=f"Unknown service: '{service_name}'",
                error_code="SERVICE_NOT_FOUND",
            )


class ClearDnsCacheToolInput(ToolInputSchema):
    """Input schema for clear_dns_cache tool."""
    scope: str = "client"


class ClearDnsCacheTool(Tool):
    """
    Clear DNS cache to resolve name resolution issues.

    Risk Level: LOW
    Approval Required: No

    Simulates clearing DNS cache.
    """

    name = "clear_dns_cache"
    description = "Clear DNS cache to resolve name resolution issues"
    input_schema = ClearDnsCacheToolInput
    risk_level = RiskLevel.LOW
    approval_required = False

    def __init__(self, simulated_state: dict = None):
        super().__init__(simulated_state)

        if "dns_cache" not in self.simulated_state:
            self.simulated_state["dns_cache"] = {
                "entries": [],
                "last_cleared": None,
            }

    def execute(self, scope: str = "client") -> ToolResult:
        """
        Clear DNS cache.

        Args:
            scope: Scope of cache clear (client, server, all)

        Returns:
            ToolResult with clear confirmation
        """
        self.simulated_state["dns_cache"]["entries"] = []
        self.simulated_state["dns_cache"]["last_cleared"] = "2026-10-01T10:30:00Z"

        return ToolResult(
            success=True,
            tool=self.name,
            status="success",
            message=f"DNS cache cleared ({scope} scope)",
            data={
                "scope": scope,
                "entries_cleared": 0,
                "last_cleared": "2026-10-01T10:30:00Z",
            },
        )


class ClearOutlookCacheToolInput(ToolInputSchema):
    """Input schema for clear_outlook_cache tool."""
    user_id: str = "unknown"
    scope: str = "cache_only"


class ClearOutlookCacheTool(Tool):
    """
    Clear Outlook cache to resolve sync issues.

    Risk Level: LOW
    Approval Required: No

    Simulates clearing Outlook cache for email sync issues.
    """

    name = "clear_outlook_cache"
    description = "Clear Outlook cache to resolve sync issues"
    input_schema = ClearOutlookCacheToolInput
    risk_level = RiskLevel.LOW
    approval_required = False

    def __init__(self, simulated_state: dict = None):
        super().__init__(simulated_state)

        if "outlook_cache" not in self.simulated_state:
            self.simulated_state["outlook_cache"] = {
                "users": {},
                "last_cleared": None,
            }

    def execute(self, user_id: str = "unknown", scope: str = "cache_only") -> ToolResult:
        """
        Clear Outlook cache.

        Args:
            user_id: User identifier
            scope: Scope of cache clear

        Returns:
            ToolResult with clear confirmation
        """
        if user_id not in self.simulated_state["outlook_cache"]["users"]:
            self.simulated_state["outlook_cache"]["users"][user_id] = {"cache_size": 0}

        self.simulated_state["outlook_cache"]["users"][user_id]["cache_size"] = 0
        self.simulated_state["outlook_cache"]["last_cleared"] = "2026-10-01T10:30:00Z"

        return ToolResult(
            success=True,
            tool=self.name,
            status="success",
            message=f"Outlook cache cleared for user '{user_id}'",
            data={
                "user_id": user_id,
                "scope": scope,
                "cache_cleared": True,
                "last_cleared": "2026-10-01T10:30:00Z",
            },
        )
