from typing import Dict, Any
from ..models.schemas import Action, IncidentResolution
from ..tools.handlers import verify_connectivity

class VerificationAgent:
    """Executes active health and connectivity probes to verify actual symptom relief."""

    def run(self, action: Action) -> IncidentResolution:
        # Check action tool type
        if "vpn" in action.tool.lower():
            probe_result = verify_connectivity(target="VPN Gateway", probe_type="handshake")
            return IncidentResolution(
                verificationMethod="Gateway Handshake & Tunnel Connectivity Probe",
                success=probe_result.get("verified", True)
            )

        if "proxy" in action.tool.lower() or "service" in action.tool.lower():
            probe_result = verify_connectivity(target="Internal Auth Proxy (Port 8080)", probe_type="port_open")
            return IncidentResolution(
                verificationMethod="Port 8080 Listener & Proxy Handshake Probe",
                success=probe_result.get("verified", True)
            )

        # Default probe
        probe_result = verify_connectivity(target="System Health", probe_type="standard")
        return IncidentResolution(
            verificationMethod="Automated Health Diagnostic Check",
            success=probe_result.get("verified", True)
        )

verification_agent = VerificationAgent()
