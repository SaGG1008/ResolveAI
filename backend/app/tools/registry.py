from typing import Dict, Any, Callable
from ..models.schemas import RiskLevel

class ToolDefinition:
    def __init__(
        self,
        name: str,
        description: str,
        risk_level: RiskLevel,
        requires_approval: bool,
        handler: Callable[..., Dict[str, Any]]
    ):
        self.name = name
        self.description = description
        self.risk_level = risk_level
        self.requires_approval = requires_approval
        self.handler = handler

class ToolRegistry:
    def __init__(self):
        self._tools: Dict[str, ToolDefinition] = {}

    def register(
        self,
        name: str,
        description: str,
        risk_level: RiskLevel,
        requires_approval: bool
    ):
        def decorator(func: Callable[..., Dict[str, Any]]):
            self._tools[name] = ToolDefinition(
                name=name,
                description=description,
                risk_level=risk_level,
                requires_approval=requires_approval,
                handler=func
            )
            return func
        return decorator

    def get_tool(self, name: str) -> ToolDefinition:
        if name not in self._tools:
            raise ValueError(f"Tool '{name}' is not in the allowlisted tool registry.")
        return self._tools[name]

    def list_tools(self) -> Dict[str, Dict[str, Any]]:
        return {
            name: {
                "name": tool.name,
                "description": tool.description,
                "risk_level": tool.risk_level,
                "requires_approval": tool.requires_approval
            }
            for name, tool in self._tools.items()
        }

    def execute(self, name: str, **kwargs) -> Dict[str, Any]:
        tool = self.get_tool(name)
        return tool.handler(**kwargs)

tool_registry = ToolRegistry()
