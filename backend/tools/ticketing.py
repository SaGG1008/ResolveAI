"""
Ticketing tools for ResolveAI.
"""

from .base import Tool, ToolInputSchema, ToolResult, RiskLevel


class CreateTicketToolInput(ToolInputSchema):
    """Input schema for create_ticket tool."""
    summary: str
    description: str
    priority: str = "medium"
    category: str = "General"
    evidence_ids: list[str] = None


class CreateTicketTool(Tool):
    """
    Create a new ticket for human review.

    Risk Level: MEDIUM
    Approval Required: No

    Simulates creating a ticket in the ticketing system.
    """

    name = "create_ticket"
    description = "Create a new ticket for human review and tracking"
    input_schema = CreateTicketToolInput
    risk_level = RiskLevel.MEDIUM
    approval_required = False

    def __init__(self, simulated_state: dict = None):
        super().__init__(simulated_state)

        if "tickets" not in self.simulated_state:
            self.simulated_state["tickets"] = []
            self.simulated_state["_ticket_counter"] = 0

    def execute(self, summary: str, description: str, priority: str = "medium", category: str = "General", evidence_ids: list[str] = None) -> ToolResult:
        """
        Create a new ticket.

        Args:
            summary: Brief summary of the issue
            description: Detailed description
            priority: Ticket priority (low, medium, high, critical)
            category: Ticket category
            evidence_ids: Optional list of evidence IDs to link

        Returns:
            ToolResult with ticket creation confirmation
        """
        self.simulated_state["_ticket_counter"] = self.simulated_state.get("_ticket_counter", 0) + 1
        ticket_id = f"TICK-{self.simulated_state['_ticket_counter']:04d}"

        ticket = {
            "id": ticket_id,
            "summary": summary,
            "description": description,
            "priority": priority,
            "category": category,
            "status": "new",
            "evidence_ids": evidence_ids or [],
            "created_at": "2026-10-01T10:30:00Z",
            "assignee": None,
        }

        self.simulated_state["tickets"].append(ticket)

        return ToolResult(
            success=True,
            tool=self.name,
            status="success",
            message=f"Ticket '{ticket_id}' created successfully",
            data={
                "ticket_id": ticket_id,
                "ticket": ticket,
            },
        )


class EscalateToHumanToolInput(ToolInputSchema):
    """Input schema for escalate_to_human tool."""
    reason: str
    urgency: str = "standard"
    affected_users: int = 1
    evidence_ids: list[str] = None


class EscalateToHumanTool(Tool):
    """
    Escalate an incident to human review.

    Risk Level: HIGH
    Approval Required: No (escalation itself is the approval flow)

    Simulates escalating an incident to the human support team.
    """

    name = "escalate_to_human"
    description = "Escalate an incident to human review for complex issues"
    input_schema = EscalateToHumanToolInput
    risk_level = RiskLevel.HIGH
    approval_required = False

    def __init__(self, simulated_state: dict = None):
        super().__init__(simulated_state)

        if "escalations" not in self.simulated_state:
            self.simulated_state["escalations"] = []
            self.simulated_state["_escalation_counter"] = 0

    def execute(self, reason: str, urgency: str = "standard", affected_users: int = 1, evidence_ids: list[str] = None) -> ToolResult:
        """
        Escalate an incident to human review.

        Args:
            reason: Reason for escalation
            urgency: Urgency level (standard, high, critical)
            affected_users: Number of affected users
            evidence_ids: Optional list of evidence IDs

        Returns:
            ToolResult with escalation confirmation
        """
        self.simulated_state["_escalation_counter"] = self.simulated_state.get("_escalation_counter", 0) + 1
        escalation_id = f"ESC-{self.simulated_state['_escalation_counter']:04d}"

        escalation = {
            "id": escalation_id,
            "reason": reason,
            "urgency": urgency,
            "affected_users": affected_users,
            "evidence_ids": evidence_ids or [],
            "status": "pending_review",
            "created_at": "2026-10-01T10:30:00Z",
            "assigned_to": None,
        }

        self.simulated_state["escalations"].append(escalation)

        return ToolResult(
            success=True,
            tool=self.name,
            status="success",
            message=f"Incident escalated to human review (escalation ID: {escalation_id})",
            data={
                "escalation_id": escalation_id,
                "urgency": urgency,
                "escalation": escalation,
            },
        )
