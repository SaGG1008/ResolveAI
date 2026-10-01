"""
Knowledge base tools for ResolveAI.
"""

from typing import Optional
from .base import Tool, ToolInputSchema, ToolResult, RiskLevel


class SearchKnowledgeBaseToolInput(ToolInputSchema):
    """Input schema for search_knowledge_base tool."""
    query: str
    category: Optional[str] = None


class SearchKnowledgeBaseTool(Tool):
    """
    Search the knowledge base for relevant articles.

    Risk Level: LOW
    Approval Required: No

    This tool searches through documented procedures and known issues.
    """

    name = "search_knowledge_base"
    description = "Search the knowledge base for relevant articles and procedures"
    input_schema = SearchKnowledgeBaseToolInput
    risk_level = RiskLevel.LOW
    approval_required = False

    def __init__(self, simulated_state: dict = None):
        super().__init__(simulated_state)

        # Mock knowledge base
        self._kb = [
            {
                "id": "kb_vpn_001",
                "title": "VPN Token Expiration Issues",
                "content": "When VPN tokens expire, users cannot authenticate to corporate network. Solution: Reset VPN token via admin console.",
                "category": "VPN",
                "keywords": ["vpn", "token", "authentication", "cannot connect", "expired"],
            },
            {
                "id": "kb_vpn_002",
                "title": "VPN Connection Troubleshooting",
                "content": "Common VPN issues include network connectivity, certificate errors, and token expiration. Check system status first.",
                "category": "VPN",
                "keywords": ["vpn", "connection", "troubleshoot", "network", "certificate"],
            },
            {
                "id": "kb_email_001",
                "title": "Outlook Email Sync Issues",
                "content": "Email delays are commonly caused by cache corruption. Clear Outlook cache to resolve sync issues.",
                "category": "Email",
                "keywords": ["email", "outlook", "sync", "delay", "cache"],
            },
            {
                "id": "kb_email_002",
                "title": "Exchange Server Connection",
                "content": "Exchange connection failures may require server restart or mailbox repair. Check service status.",
                "category": "Email",
                "keywords": ["exchange", "connection", "server", "mailbox"],
            },
        ]

    def execute(self, query: str, category: Optional[str] = None) -> ToolResult:
        """
        Search the knowledge base for relevant articles.

        Args:
            query: Search query string
            category: Optional category filter

        Returns:
            ToolResult with matching articles
        """
        query_lower = query.lower()

        # Filter articles by category if specified
        articles = self._kb
        if category:
            articles = [a for a in articles if a["category"].lower() == category.lower()]

        # Score and filter articles by relevance
        results = []
        for article in articles:
            score = 0
            for keyword in article.get("keywords", []):
                if keyword in query_lower:
                    score += 10
            if article["title"].lower() in query_lower:
                score += 20

            if score > 0:
                results.append({
                    "id": article["id"],
                    "title": article["title"],
                    "content": article["content"],
                    "relevance": min(score, 100),
                    "category": article["category"],
                })

        # Sort by relevance
        results.sort(key=lambda x: x["relevance"], reverse=True)

        return ToolResult(
            success=True,
            tool=self.name,
            status="success",
            message=f"Found {len(results)} relevant knowledge base article(s)",
            data={"articles": results},
        )


class SearchPreviousTicketsToolInput(ToolInputSchema):
    """Input schema for search_previous_tickets tool."""
    query: str
    status_filter: Optional[str] = None


class SearchPreviousTicketsTool(Tool):
    """
    Search previous incident tickets for similar issues.

    Risk Level: LOW
    Approval Required: No

    This tool searches historical tickets to identify resolution patterns.
    """

    name = "search_previous_tickets"
    description = "Search previous incident tickets for similar issues and resolutions"
    input_schema = SearchPreviousTicketsToolInput
    risk_level = RiskLevel.LOW
    approval_required = False

    def __init__(self, simulated_state: dict = None):
        super().__init__(simulated_state)

        # Mock ticket history
        self._tickets = [
            {
                "id": "TICK-001",
                "title": "VPN Authentication Failed - john.doe",
                "description": "User john.doe unable to authenticate to VPN. Got 'invalid token' error.",
                "category": "VPN",
                "status": "resolved",
                "resolution": "VPN token was reset. User successfully authenticated.",
                "resolution_time_minutes": 5,
            },
            {
                "id": "TICK-002",
                "title": "Outlook Email Sync Delay",
                "description": "User reports Outlook email not syncing. Messages delayed by 2+ hours.",
                "category": "Email",
                "status": "resolved",
                "resolution": "Cleared Outlook cache. Sync restored within 10 minutes.",
                "resolution_time_minutes": 10,
            },
            {
                "id": "TICK-003",
                "title": "DNS Resolution Failures",
                "description": "Users reporting inability to resolve domain names.",
                "category": "Network",
                "status": "resolved",
                "resolution": "Cleared DNS cache on client machines. Resolution restored.",
                "resolution_time_minutes": 15,
            },
            {
                "id": "TICK-004",
                "title": "Service Account Password Expired",
                "description": "Background service failing due to expired credentials.",
                "category": "Security",
                "status": "resolved",
                "resolution": "Service account password reset. Service restored.",
                "resolution_time_minutes": 20,
            },
        ]

    def execute(self, query: str, status_filter: Optional[str] = None) -> ToolResult:
        """
        Search previous tickets for similar issues.

        Args:
            query: Search query string
            status_filter: Optional status filter (resolved, open, etc.)

        Returns:
            ToolResult with matching tickets
        """
        query_lower = query.lower()

        # Filter tickets by status if specified
        tickets = self._tickets
        if status_filter:
            tickets = [t for t in tickets if t["status"].lower() == status_filter.lower()]

        # Score and filter tickets by relevance
        results = []
        for ticket in tickets:
            score = 0
            combined_text = (ticket["title"] + " " + ticket["description"]).lower()
            for keyword in query_lower.split():
                if keyword in combined_text:
                    score += 5

            if score > 0:
                results.append({
                    "id": ticket["id"],
                    "title": ticket["title"],
                    "description": ticket["description"],
                    "category": ticket["category"],
                    "status": ticket["status"],
                    "resolution": ticket["resolution"],
                    "resolution_time_minutes": ticket["resolution_time_minutes"],
                    "relevance": min(score, 100),
                })

        # Sort by relevance
        results.sort(key=lambda x: x["relevance"], reverse=True)

        return ToolResult(
            success=True,
            tool=self.name,
            status="success",
            message=f"Found {len(results)} matching ticket(s)",
            data={"tickets": results},
        )


class GetTroubleshootingProcedureToolInput(ToolInputSchema):
    """Input schema for get_troubleshooting_procedure tool."""
    issue_type: str


class GetTroubleshootingProcedureTool(Tool):
    """
    Get step-by-step troubleshooting procedures for issue types.

    Risk Level: LOW
    Approval Required: No

    This tool retrieves documented procedures for common issues.
    """

    name = "get_troubleshooting_procedure"
    description = "Get step-by-step troubleshooting procedures for specific issue types"
    input_schema = GetTroubleshootingProcedureToolInput
    risk_level = RiskLevel.LOW
    approval_required = False

    def __init__(self, simulated_state: dict = None):
        super().__init__(simulated_state)

        # Mock procedures
        self._procedures = {
            "vpn": {
                "title": "VPN Token Reset Procedure",
                "description": "Reset VPN token for user experiencing authentication issues",
                "steps": [
                    "Navigate to VPN Admin Console",
                    "Locate user account",
                    "Click 'Reset Token' button",
                    "User will receive new token via email",
                    "Verify successful authentication",
                ],
                "risk": "Low",
                "expected_outcome": "User can authenticate to VPN with new token",
            },
            "email": {
                "title": "Outlook Cache Clear Procedure",
                "description": "Clear Outlook cache to resolve sync issues",
                "steps": [
                    "Close Outlook application",
                    "Navigate to AppData\\Local\\Microsoft\\Outlook",
                    "Delete .ost files",
                    "Restart Outlook",
                    "Verify email sync is working",
                ],
                "risk": "Low",
                "expected_outcome": "Email sync restored",
            },
            "dns": {
                "title": "DNS Cache Clear Procedure",
                "description": "Clear DNS cache to resolve name resolution issues",
                "steps": [
                    "Open Command Prompt as Administrator",
                    "Run 'ipconfig /flushdns'",
                    "Verify DNS resolution with 'nslookup example.com'",
                    "Check if issue is resolved",
                ],
                "risk": "Low",
                "expected_outcome": "DNS resolution working",
            },
            "service": {
                "title": "Service Restart Procedure",
                "description": "Restart a service to resolve operational issues",
                "steps": [
                    "Open Services console (services.msc)",
                    "Locate the service",
                    "Right-click and select 'Restart'",
                    "Verify service is running",
                    "Test service functionality",
                ],
                "risk": "Medium",
                "expected_outcome": "Service restored to operational state",
            },
        }

    def execute(self, issue_type: str) -> ToolResult:
        """
        Get troubleshooting procedure for issue type.

        Args:
            issue_type: Type of issue (vpn, email, dns, service, etc.)

        Returns:
            ToolResult with procedure steps
        """
        issue_lower = issue_type.lower()

        # Find matching procedure
        for key, procedure in self._procedures.items():
            if key in issue_lower:
                return ToolResult(
                    success=True,
                    tool=self.name,
                    status="success",
                    message=f"Retrieved procedure for '{key}' issues",
                    data={"procedure": procedure},
                )

        # No matching procedure found
        return ToolResult(
            success=False,
            tool=self.name,
            status="failure",
            message=f"No procedure found for issue type: '{issue_type}'",
            error_code="PROCEDURE_NOT_FOUND",
        )
