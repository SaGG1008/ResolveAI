from typing import Optional, List
from ..models.schemas import Action, Diagnosis, Evidence
from ..tools.registry import tool_registry

class ActionPlannerAgent:
    """Selects allowlisted remediation actions, calculates blast radius, and enforces approval gates."""

    def run(self, category: str, diagnosis: Diagnosis, evidence: List[Evidence]) -> Optional[Action]:
        cause = diagnosis.likelyCause.lower()

        # If confidence is low (< 60%) or hardware crash detected, do not plan automated fix -> trigger escalation
        if diagnosis.confidence < 60 or "hardware" in cause or "kernel" in cause:
            return None

        if "vpn" in cause or "session lock" in cause:
            tool_meta = tool_registry.get_tool("reset_vpn_session")
            return Action(
                id="act-vpn-reset",
                tool="reset_vpn_session",
                description="Clear stale gateway session lock and invalidate ghost token.",
                riskLevel=tool_meta.risk_level,
                requiresApproval=tool_meta.requires_approval,
                linkedEvidence=evidence,
                reasoning="Evidence shows a dead session lock on the VPN gateway. Resetting the session is low-risk and restores authentication immediately."
            )

        if "proxy" in cause or "service" in cause:
            tool_meta = tool_registry.get_tool("restart_service")
            return Action(
                id="act-proxy-restart",
                tool="restart_service(auth_proxy)",
                description="Restart the local auth_proxy daemon to reopen port 8080.",
                riskLevel="medium",
                requiresApproval=True,
                linkedEvidence=evidence,
                reasoning="Daemon crash identified on port 8080. Service restart is required, but flagged as Medium Risk because it resets active network sockets."
            )

        if "dns" in cause:
            tool_meta = tool_registry.get_tool("flush_dns_cache")
            return Action(
                id="act-dns-flush",
                tool="flush_dns_cache",
                description="Flush local resolver cache.",
                riskLevel=tool_meta.risk_level,
                requiresApproval=tool_meta.requires_approval,
                linkedEvidence=evidence,
                reasoning="Purging local DNS cache fixes stale record mappings without side effects."
            )

        return None

action_planner_agent = ActionPlannerAgent()
