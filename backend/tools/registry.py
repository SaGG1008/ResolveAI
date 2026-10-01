"""
Tool Registry for ResolveAI.

Centralized registry for all tools with:
- Tool discovery
- Validation
- Risk/permission checking
- Tool selection by agents
"""

from typing import Dict, Type
from .base import Tool, RiskLevel, ToolResult, ToolResultStatus
from .risk_policy import risk_policy
from .knowledge import SearchKnowledgeBaseTool, SearchPreviousTicketsTool, GetTroubleshootingProcedureTool
from .diagnostics import GetSystemStatusTool
from .remediation import ResetVpnTokenTool, RestartServiceTool, ClearDnsCacheTool
from .ticketing import CreateTicketTool, EscalateToHumanTool
from .verification import VerifyResolutionTool


class ToolRegistry:
    """
    Centralized registry for all ResolveAI tools.

    Provides:
    - Tool discovery and listing
    - Input validation
    - Risk/permission checking
    - Tool selection by agents
    - Secure tool execution
    """

    def __init__(self, simulated_state: Dict[str, any] = None):
        """
        Initialize the tool registry.

        Args:
            simulated_state: Shared state for the simulated enterprise environment.
        """
        self.simulated_state = simulated_state or {}
        self._tools: Dict[str, Tool] = {}
        self._register_all_tools()

    def _register_all_tools(self) -> None:
        """Register all available tools."""
        # Knowledge tools
        self.register_tool(
            SearchKnowledgeBaseTool(self.simulated_state)
        )
        self.register_tool(
            SearchPreviousTicketsTool(self.simulated_state)
        )
        self.register_tool(
            GetTroubleshootingProcedureTool(self.simulated_state)
        )

        # Diagnostics tools
        self.register_tool(
            GetSystemStatusTool(self.simulated_state)
        )

        # Remediation tools
        self.register_tool(
            ResetVpnTokenTool(self.simulated_state)
        )
        self.register_tool(
            RestartServiceTool(self.simulated_state)
        )
        self.register_tool(
            ClearDnsCacheTool(self.simulated_state)
        )

        # Ticketing tools
        self.register_tool(
            CreateTicketTool(self.simulated_state)
        )
        self.register_tool(
            EscalateToHumanTool(self.simulated_state)
        )

        # Verification tools
        self.register_tool(
            VerifyResolutionTool(self.simulated_state)
        )

    def register_tool(self, tool: Tool) -> None:
        """
        Register a tool with the registry.

        Args:
            tool: Tool instance to register
        """
        if tool.name in self._tools:
            raise ValueError(f"Tool '{tool.name}' is already registered")
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> Tool:
        """
        Get a tool by name.

        Args:
            name: Name of the tool

        Returns:
            Tool instance

        Raises:
            ValueError: If tool is not found
        """
        if name not in self._tools:
            raise ValueError(f"Unknown tool: '{name}'")
        return self._tools[name]

    def list_tools(self) -> list[dict]:
        """
        List all registered tools with metadata.

        Returns:
            List of tool metadata dictionaries
        """
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "risk_level": tool.risk_level.value,
                "approval_required": tool.approval_required,
            }
            for tool in self._tools.values()
        ]

    def get_tools_by_category(self) -> Dict[str, list[dict]]:
        """
        Get tools organized by category.

        Returns:
            Dict mapping category names to tool lists
        """
        categories = {
            "Knowledge": [],
            "Diagnostics": [],
            "Remediation": [],
            "Ticketing": [],
            "Verification": [],
        }

        for tool in self._tools.values():
            category = self._categorize_tool(tool.name)
            if category in categories:
                categories[category].append({
                    "name": tool.name,
                    "description": tool.description,
                    "risk_level": tool.risk_level.value,
                    "approval_required": tool.approval_required,
                })

        return categories

    def _categorize_tool(self, name: str) -> str:
        """Categorize a tool by name."""
        if "knowledge" in name.lower() or "ticket" in name.lower() or "procedure" in name.lower():
            return "Knowledge"
        elif "status" in name.lower() or "health" in name.lower():
            return "Diagnostics"
        elif "reset" in name.lower() or "restart" in name.lower() or "clear" in name.lower():
            return "Remediation"
        elif "ticket" in name.lower() or "escalate" in name.lower():
            return "Ticketing"
        elif "verify" in name.lower() or "resolution" in name.lower():
            return "Verification"
        else:
            return "Remediation"

    def execute_tool(self, name: str, **kwargs) -> ToolResult:
        """
        Execute a tool with validation.

        Args:
            name: Name of the tool to execute
            **kwargs: Parameters for the tool

        Returns:
            ToolResult with standardized structure
        """
        # Find the tool
        tool = self.get_tool(name)

        # Validate inputs
        try:
            validated_inputs = tool.validate_inputs(**kwargs)
        except ValueError as e:
            return ToolResult(
                success=False,
                tool=name,
                status=ToolResultStatus.FAILURE,
                message=str(e),
                error_code="INVALID_INPUTS",
            )

        # Check approval requirement
        if risk_policy.requires_approval(tool.name, tool.risk_level):
            return ToolResult(
                success=False,
                tool=name,
                status=ToolResultStatus.ESCALATED,
                message=f"Tool '{name}' requires human approval before execution",
                error_code="APPROVAL_REQUIRED",
            )

        # Execute the tool
        result = tool.execute(**validated_inputs)

        # Update state if successful
        if result.success and hasattr(tool, 'update_state'):
            tool.update_state(f"{name}_last_run", "success")

        return result

    def select_tool(self, incident_description: str, category: str) -> Optional[dict]:
        """
        Select an appropriate tool based on incident description.

        This is used by the Action Planner agent to find a suitable tool.

        Args:
            incident_description: Description of the incident
            category: Incident category (VPN, Email, Security, etc.)

        Returns:
            Tool selection metadata or None if no suitable tool found
        """
        # Score each tool based on description match
        scored_tools = []

        for tool in self._tools.values():
            score = self._calculate_tool_score(tool, incident_description, category)
            if score > 0:
                scored_tools.append((score, tool))

        if not scored_tools:
            return None

        # Return the highest-scoring tool
        scored_tools.sort(key=lambda x: x[0], reverse=True)
        best_tool = scored_tools[0][1]

        return {
            "name": best_tool.name,
            "description": best_tool.description,
            "risk_level": best_tool.risk_level.value,
            "approval_required": best_tool.approval_required,
            "score": scored_tools[0][0],
        }

    def _calculate_tool_score(self, tool: Tool, description: str, category: str) -> int:
        """
        Calculate how well a tool matches an incident description.

        Args:
            tool: Tool to score
            description: Incident description
            category: Incident category

        Returns:
            Match score (0 = no match, higher = better match)
        """
        score = 0
        description_lower = description.lower()
        category_lower = category.lower()

        # Category-based scoring
        if category_lower == "vpn" and "vpn" in tool.name.lower():
            score += 50
        elif category_lower == "email" and "email" in tool.name.lower():
            score += 50
        elif category_lower == "security" and "security" in tool.name.lower():
            score += 50

        # Description keyword matching
        keywords = {
            "reset_vpn_token": ["vpn", "token", "authentication", "reset"],
            "restart_service": ["service", "restart", "stop", "start", "fail"],
            "clear_dns_cache": ["dns", "cache", "resolve", "domain"],
            "create_ticket": ["create", "ticket", "escalate", "human"],
            "escalate_to_human": ["escalate", "human", "security", "urgent"],
            "verify_resolution": ["verify", "success", "confirm", "resolution"],
        }

        tool_keywords = keywords.get(tool.name, [])
        for keyword in tool_keywords:
            if keyword in description_lower:
                score += 10

        return score
