"""
Diagnostics tools for ResolveAI.
"""

from typing import Optional
from .base import Tool, ToolInputSchema, ToolResult, RiskLevel


class GetSystemStatusToolInput(ToolInputSchema):
    """Input schema for get_system_status tool."""
    service: Optional[str] = None


class GetSystemStatusTool(Tool):
    """
    Get current status of enterprise services.

    Risk Level: LOW
    Approval Required: No

    This tool checks the operational status of services in the simulated environment.
    """

    name = "get_system_status"
    description = "Get current operational status of enterprise services"
    input_schema = GetSystemStatusToolInput
    risk_level = RiskLevel.LOW
    approval_required = False

    def __init__(self, simulated_state: dict = None):
        super().__init__(simulated_state)

        # Initialize simulated service state
        if "services" not in self.simulated_state:
            self.simulated_state["services"] = {
                "vpn_auth": {
                    "name": "VPN Authentication",
                    "status": "operational",
                    "last_check": "2026-10-01T10:00:00Z",
                    "uptime_percentage": 99.9,
                },
                "email_exchange": {
                    "name": "Exchange Email",
                    "status": "operational",
                    "last_check": "2026-10-01T10:00:00Z",
                    "uptime_percentage": 99.8,
                },
                "security_monitoring": {
                    "name": "Security Monitoring",
                    "status": "operational",
                    "last_check": "2026-10-01T10:00:00Z",
                    "uptime_percentage": 99.99,
                },
                "dns_resolver": {
                    "name": "DNS Resolution",
                    "status": "operational",
                    "last_check": "2026-10-01T10:00:00Z",
                    "uptime_percentage": 99.5,
                },
            }

    def execute(self, service: Optional[str] = None) -> ToolResult:
        """
        Get system status, optionally for a specific service.

        Args:
            service: Optional service name to check

        Returns:
            ToolResult with service status information
        """
        services = self.simulated_state.get("services", {})

        if service:
            # Check specific service
            service_key = service.lower().replace(" ", "_")
            if service_key in services:
                return ToolResult(
                    success=True,
                    tool=self.name,
                    status="success",
                    message=f"Service '{services[service_key]['name']}' is {services[service_key]['status']}",
                    data={"service": services[service_key]},
                )
            else:
                return ToolResult(
                    success=False,
                    tool=self.name,
                    status="failure",
                    message=f"Unknown service: '{service}'",
                    error_code="SERVICE_NOT_FOUND",
                )
        else:
            # Return all services
            return ToolResult(
                success=True,
                tool=self.name,
                status="success",
                message="Retrieved status for all services",
                data={"services": services, "total_operational": len([s for s in services.values() if s["status"] == "operational"]), "total_services": len(services)},
            )
