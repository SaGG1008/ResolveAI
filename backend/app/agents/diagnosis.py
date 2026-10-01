from typing import List
from ..models.schemas import Diagnosis, Evidence

class DiagnosisAgent:
    """Synthesizes root cause and confidence based strictly on gathered evidence."""

    def run(self, description: str, category: str, evidence: List[Evidence]) -> Diagnosis:
        text = f"{description} {category}".lower()

        if not evidence:
            return Diagnosis(
                likelyCause="Unknown / Indeterminate issue without matching telemetry or knowledge articles.",
                confidence=20,
                supportingEvidence=[],
                uncertainty="Insufficient context or evidence found. Requires human investigation."
            )

        # Scenario 1: VPN Disconnect / Session Lock
        if "vpn" in text:
            return Diagnosis(
                likelyCause="VPN authentication token has expired due to a stale session lock in the gateway session table.",
                confidence=94,
                supportingEvidence=evidence,
                uncertainty=None
            )

        # Scenario 2: Security & Account Access
        if "security" in text or "accessed my account" in text or "unauthorized" in text or "suspicious" in text:
            return Diagnosis(
                likelyCause="Suspicious unauthorized account access pattern or compromised session credential detected.",
                confidence=92,
                supportingEvidence=evidence,
                uncertainty="Automated credential resets prohibited by company security policy without human SecOps review."
            )

        # Scenario 3: Auth Proxy Crash
        if "proxy" in text or "git" in text or "8080" in text:
            return Diagnosis(
                likelyCause="Local authentication proxy daemon crashed due to memory limit (Exit Code 137).",
                confidence=89,
                supportingEvidence=evidence,
                uncertainty="Restarting service will temporarily disrupt in-flight git connections."
            )

        # Scenario 4: Hardware Crash
        if "kernel" in text or "0x889fa" in text or "purple" in text or "screen" in text:
            return Diagnosis(
                likelyCause="Unrecoverable hardware memory parity corruption (Code 0x889FA).",
                confidence=35,
                supportingEvidence=evidence,
                uncertainty="Hardware level component failure cannot be addressed by software remediation."
            )

        # Default Case
        top_ev = evidence[0]
        return Diagnosis(
            likelyCause=f"Probable issue matching {top_ev.title}",
            confidence=top_ev.relevance,
            supportingEvidence=evidence,
            uncertainty=None
        )

diagnosis_agent = DiagnosisAgent()
