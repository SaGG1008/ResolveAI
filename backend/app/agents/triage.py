from typing import Dict, Any, Tuple
from ..models.schemas import PriorityLevel

class TriageAgent:
    """Classifies incoming natural language issue, identifies category & priority."""

    def run(self, description: str, title: str = "") -> Dict[str, Any]:
        text = f"{title} {description}".lower()

        # Category and Priority determination
        if any(w in text for w in ["vpn", "tunnel", "globalprotect", "cisco", "anyconnect", "disconnect"]):
            category = "Network / VPN"
            priority: PriorityLevel = "high"
            hypothesis = "VPN connectivity disruption or stale authentication session lock"
        elif any(w in text for w in ["proxy", "git", "port 8080", "connection refused", "internal mirror", "mirror"]):
            category = "Services"
            priority = "medium"
            hypothesis = "Internal auth proxy service interruption on port 8080"
        elif any(w in text for w in ["kernel", "panic", "blue screen", "bsod", "purple", "flicker", "screen", "0x889fa", "hardware"]):
            category = "Hardware"
            priority = "critical"
            hypothesis = "Critical physical hardware failure or kernel memory corruption"
        elif any(w in text for w in ["dns", "domain", "lookup", "resolve"]):
            category = "Network"
            priority = "medium"
            hypothesis = "DNS cache corruption or resolver mapping failure"
        elif any(w in text for w in ["password", "sso", "okta", "login", "auth"]):
            category = "Authentication"
            priority = "medium"
            hypothesis = "Authentication token invalidation or identity session loop"
        else:
            category = "General IT"
            priority = "low"
            hypothesis = "General user workstation inquiry"

        generated_title = title if title else description[:60] + ("..." if len(description) > 60 else "")

        return {
            "title": generated_title,
            "category": category,
            "priority": priority,
            "hypothesis": hypothesis,
            "message": f"Triage complete: Classified as '{category}' with priority '{priority.upper()}'. Hypothesis: {hypothesis}."
        }

triage_agent = TriageAgent()
