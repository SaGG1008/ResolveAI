from typing import Dict, Any, Optional
from ..models.schemas import PriorityLevel, TriageResult

class TriageAgent:
    """Classifies incoming natural language issue, identifies category, priority & affected service."""

    def run(self, description: str, title: str = "") -> TriageResult:
        text = f"{title} {description}".lower()

        # Category, Priority and Affected Service determination
        if any(w in text for w in ["accessed my account", "unauthorized", "suspicious login", "compromised", "hacked", "security alert"]):
            category = "Security"
            priority: PriorityLevel = "critical"
            affected_service = "Okta Enterprise SSO & SecOps Auth Guard"
            hypothesis = "Potential credential compromise or unauthorized session activity"
        elif any(w in text for w in ["vpn", "tunnel", "globalprotect", "cisco", "anyconnect", "disconnect"]):
            category = "Network / VPN"
            priority: PriorityLevel = "high"
            affected_service = "Enterprise VPN Gateway (GlobalProtect)"
            hypothesis = "VPN connectivity disruption or expired authentication token / session lock"
        elif any(w in text for w in ["proxy", "git", "port 8080", "connection refused", "internal mirror", "mirror"]):
            category = "Services"
            priority = "medium"
            affected_service = "Internal Auth Proxy Daemon (Port 8080)"
            hypothesis = "Internal auth proxy service interruption on port 8080"
        elif any(w in text for w in ["kernel", "panic", "blue screen", "bsod", "purple", "flicker", "screen", "0x889fa", "hardware"]):
            category = "Hardware"
            priority = "critical"
            affected_service = "Workstation Motherboard / GPU / RAM Hardware"
            hypothesis = "Critical physical hardware failure or kernel memory corruption"
        elif any(w in text for w in ["dns", "domain", "lookup", "resolve"]):
            category = "Network"
            priority = "medium"
            affected_service = "Corporate Core DNS Resolvers"
            hypothesis = "DNS cache corruption or resolver mapping failure"
        elif any(w in text for w in ["password", "sso", "okta", "login", "auth"]):
            category = "Authentication"
            priority = "medium"
            affected_service = "Okta Enterprise Single Sign-On"
            hypothesis = "Authentication token invalidation or identity session loop"
        else:
            category = "General IT"
            priority = "low"
            affected_service = "General Workstation"
            hypothesis = "General user workstation inquiry"

        generated_title = title if title else description[:60] + ("..." if len(description) > 60 else "")

        return TriageResult(
            title=generated_title,
            category=category,
            priority=priority,
            affectedService=affected_service,
            hypothesis=hypothesis,
            message=f"Triage complete: Classified as '{category}' ({priority.upper()} priority). Affected service: {affected_service}. Hypothesis: {hypothesis}."
        )

triage_agent = TriageAgent()
