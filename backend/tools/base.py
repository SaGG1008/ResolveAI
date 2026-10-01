"""
Base classes for ResolveAI tools.

All tools must implement the Tool interface with:
- name
- description
- input_schema
- output_schema
- risk_level
- approval_required
- execute()
"""

from abc import ABC, abstractmethod
from enum import Enum
from typing import Any, Optional, Dict
from pydantic import BaseModel


class RiskLevel(str, Enum):
    """Risk levels for tool execution."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"
    UNKNOWN = "unknown"


class ToolResultStatus(str, Enum):
    """Status of tool execution."""
    SUCCESS = "success"
    FAILURE = "failure"
    PENDING = "pending"
    ESCALATED = "escalated"


class ToolResult(BaseModel):
    """Standardized tool execution result."""
    success: bool
    tool: str
    status: ToolResultStatus
    message: str
    data: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None
    timestamp: str


class ToolInputSchema(BaseModel):
    """Base schema for tool inputs."""
    pass


class Tool(ABC):
    """
    Base class for all ResolveAI tools.

    Every tool must implement:
    - A predictable name for the agent to select
    - Input validation schema
    - Risk level classification
    - Approval requirement flag
    - Structured execution result
    """

    name: str = ""
    description: str = ""
    input_schema: type[ToolInputSchema] = ToolInputSchema
    risk_level: RiskLevel = RiskLevel.LOW
    approval_required: bool = False
    allows_self_verification: bool = False

    def __init__(self, simulated_state: Optional[Dict[str, Any]] = None):
        """
        Initialize tool with optional simulated state.

        Args:
            simulated_state: Shared state for the simulated enterprise environment.
                           Tools can read from and write to this state.
        """
        self.simulated_state = simulated_state or {}

    @abstractmethod
    def execute(self, **kwargs) -> ToolResult:
        """
        Execute the tool with validated inputs.

        Args:
            **kwargs: Validated inputs matching input_schema

        Returns:
            ToolResult with standardized structure
        """
        raise NotImplementedError

    def validate_inputs(self, **kwargs) -> Dict[str, Any]:
        """
        Validate inputs against schema.

        Args:
            **kwargs: Raw inputs from agent

        Returns:
            Validated and transformed inputs

        Raises:
            ValueError: If inputs don't match schema
        """
        try:
            return self.input_schema(**kwargs).model_dump()
        except Exception as e:
            raise ValueError(f"Invalid inputs for {self.name}: {e}")

    def check_approval(self, risk_level: Optional[RiskLevel] = None) -> bool:
        """
        Check if human approval is required for this tool.

        Args:
            risk_level: Optional override for risk level

        Returns:
            True if approval is required, False otherwise
        """
        level = risk_level or self.risk_level
        return self.approval_required or level in [RiskLevel.HIGH, RiskLevel.CRITICAL, RiskLevel.UNKNOWN]

    def get_risk_factors(self) -> list[str]:
        """
        Return list of risk factors for this tool.

        Used for transparency and audit trails.
        """
        return []

    def update_state(self, key: str, value: Any) -> None:
        """Update the shared simulated state."""
        self.simulated_state[key] = value

    def get_state(self, key: str, default: Any = None) -> Any:
        """Get a value from the shared simulated state."""
        return self.simulated_state.get(key, default)
