from typing import Dict, Any, Callable, Optional, List
from datetime import datetime, timezone
from ..models.schemas import RiskLevel, ToolResult

class ToolDefinition:
    def __init__(
        self,
        name: str,
        description: str,
        risk_level: RiskLevel,
        requires_approval: bool,
        category: str,
        handler: Callable[..., Dict[str, Any]],
        parameter_schema: Optional[Dict[str, Any]] = None
    ):
        self.name = name
        self.description = description
        self.risk_level = risk_level
        self.requires_approval = requires_approval
        self.category = category
        self.handler = handler
        self.parameter_schema = parameter_schema or {}

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}

    def register(
        self,
        name: str,
        description: str,
        risk_level: RiskLevel = "low",
        requires_approval: bool = False,
        category: str = "General",
        parameter_schema: Optional[Dict[str, Any]] = None
    ):
        def decorator(func: Callable[..., Dict[str, Any]]):
            self._tools[name] = ToolDefinition(
                name=name,
                description=description,
                risk_level=risk_level,
                requires_approval=requires_approval,
                category=category,
                handler=func,
                parameter_schema=parameter_schema
            )
            return func
        return decorator

    def get_tool(self, name: str) -> ToolDefinition:
        if name not in self._tools:
            # Handle aliases if needed
            if name == "reset_vpn_token" and "reset_vpn_session" in self._tools:
                return self._tools["reset_vpn_session"]
            if name == "escalate_to_human" and "create_jira_escalation_ticket" in self._tools:
                return self._tools["create_jira_escalation_ticket"]
            raise ValueError(f"Tool '{name}' is not in the allowlisted tool registry.")
        return self._tools[name]

    def list_tools(self) -> Dict[str, Dict[str, Any]]:
        return {
            name: {
                "name": tool.name,
                "description": tool.description,
                "risk_level": tool.risk_level,
                "requires_approval": tool.requires_approval,
                "category": tool.category,
                "parameters": tool.parameter_schema
            }
            for name, tool in self._tools.items()
        }

    def get_tools_by_category(self) -> Dict[str, List[Dict[str, Any]]]:
        categories: Dict[str, List[Dict[str, Any]]] = {}
        for tool in self._tools.values():
            if tool.category not in categories:
                categories[tool.category] = []
            categories[tool.category].append({
                "name": tool.name,
                "description": tool.description,
                "risk_level": tool.risk_level,
                "requires_approval": tool.requires_approval,
                "parameters": tool.parameter_schema
            })
        return categories

    def requires_approval(self, name: str) -> bool:
        tool = self.get_tool(name)
        return tool.requires_approval or tool.risk_level in ["medium", "high", "critical"]

    def execute(self, name: str, **kwargs) -> Dict[str, Any]:
        tool = self.get_tool(name)
        result = tool.handler(**kwargs)
        if isinstance(result, dict) and "status" not in result:
            result["status"] = "SUCCESS"
        return result

tool_registry = ToolRegistry()
