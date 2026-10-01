"""
Integration tests for the Tool Registry.
"""

import pytest
from tools import ToolRegistry, RiskLevel, risk_policy, ToolResultStatus
from tools.base import ToolResult


class TestToolDiscovery:
    """Test tool discovery functionality."""

    def test_list_tools_returns_all_tools(self):
        """Test that list_tools returns all registered tools."""
        registry = ToolRegistry()
        tools = registry.list_tools()

        assert len(tools) == 10  # Expected number of tools
        tool_names = [t["name"] for t in tools]

        # Verify all expected tools are present
        expected_tools = [
            "search_knowledge_base",
            "search_previous_tickets",
            "get_troubleshooting_procedure",
            "get_system_status",
            "reset_vpn_token",
            "restart_service",
            "clear_dns_cache",
            "create_ticket",
            "escalate_to_human",
            "verify_resolution",
        ]

        for expected in expected_tools:
            assert expected in tool_names, f"Missing tool: {expected}"

    def test_get_tools_by_category(self):
        """Test that tools are organized by category."""
        registry = ToolRegistry()
        categories = registry.get_tools_by_category()

        expected_categories = ["Knowledge", "Diagnostics", "Remediation", "Ticketing", "Verification"]

        for category in expected_categories:
            assert category in categories, f"Missing category: {category}"
            assert isinstance(categories[category], list), f"Category {category} should be a list"


class TestInputValidation:
    """Test input validation functionality."""

    def test_invalid_tool_raises_error(self):
        """Test that requesting an invalid tool raises ValueError."""
        registry = ToolRegistry()

        with pytest.raises(ValueError, match="Unknown tool"):
            registry.get_tool("nonexistent_tool")

    def test_execute_tool_with_invalid_inputs(self):
        """Test that invalid tool inputs are rejected."""
        registry = ToolRegistry()

        # search_knowledge_base requires a query parameter
        result = registry.execute_tool("search_knowledge_base")

        assert not result.success
        assert result.error_code == "INVALID_INPUTS"


class TestToolExecution:
    """Test actual tool execution."""

    def test_reset_vpn_token_success(self):
        """Test VPN token reset tool execution."""
        registry = ToolRegistry()

        result = registry.execute_tool("reset_vpn_token", user_id="test_user_001")

        assert result.success
        assert result.status == ToolResultStatus.SUCCESS
        assert "VPN token reset" in result.message
        assert result.data is not None
        assert result.data.get("user_id") == "test_user_001"

    def test_get_system_status_all_services(self):
        """Test system status tool returns all services."""
        registry = ToolRegistry()

        result = registry.execute_tool("get_system_status")

        assert result.success
        assert result.data is not None
        assert "services" in result.data
        assert len(result.data["services"]) > 0
        assert result.data.get("total_services") == 4
        assert result.data.get("total_operational") == 4

    def test_search_knowledge_base(self):
        """Test knowledge base search tool."""
        registry = ToolRegistry()

        result = registry.execute_tool("search_knowledge_base", query="vpn token error")

        assert result.success
        assert result.data is not None
        assert "articles" in result.data
        assert len(result.data["articles"]) >= 1

    def test_search_previous_tickets(self):
        """Test previous tickets search tool."""
        registry = ToolRegistry()

        result = registry.execute_tool("search_previous_tickets", query="vpn authentication")

        assert result.success
        assert result.data is not None
        assert "tickets" in result.data


class TestRiskPolicy:
    """Test risk policy enforcement."""

    def test_risk_levels_defined(self):
        """Test that all risk levels are properly defined."""
        assert RiskLevel.LOW == "low"
        assert RiskLevel.MEDIUM == "medium"
        assert RiskLevel.HIGH == "high"
        assert RiskLevel.CRITICAL == "critical"

    def test_low_risk_no_approval(self):
        """Test that low-risk tools don't require approval."""
        assert not risk_policy.requires_approval("reset_vpn_token")

    def test_high_risk_approval_required(self):
        """Test that high-risk tools can be configured for approval."""
        # HIGH risk tools require approval when explicitly configured
        assert risk_policy.requires_approval("escalate_to_human", RiskLevel.HIGH)
        # The escalate_to_human tool has a special approval_required setting because
        # escalation itself is the approval flow


class TestEnterpriseState:
    """Test simulated enterprise state management."""

    def test_state_persistence_across_tools(self):
        """Test that state is shared across tool executions."""
        # Use a shared state dict
        shared_state = {}
        registry = ToolRegistry(shared_state)

        # Execute reset_vpn_token
        result1 = registry.execute_tool("reset_vpn_token", user_id="user1")
        assert result1.success

        # Check state was updated in registry (tools update registry.simulated_state)
        assert "users" in registry.simulated_state
        assert "vpn_tokens" in registry.simulated_state
        assert "user1" in registry.simulated_state["users"]

    def test_dns_cache_cleared_state(self):
        """Test DNS cache clear updates state."""
        shared_state = {"dns_cache": {"entries": ["entry1", "entry2"]}}
        registry = ToolRegistry(shared_state)

        result = registry.execute_tool("clear_dns_cache", scope="client")

        assert result.success
        assert len(shared_state["dns_cache"]["entries"]) == 0


class TestServiceStatus:
    """Test service status-related functionality."""

    def test_service_health_check(self):
        """Test that all services report operational status."""
        registry = ToolRegistry()

        result = registry.execute_tool("get_system_status")

        assert result.success
        services = result.data.get("services", {})

        for service_name, service_data in services.items():
            assert service_data.get("status") == "operational", f"Service {service_name} should be operational"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
