import time
import json
from pathlib import Path
from typing import Dict, Any, Optional
from .registry import tool_registry
from ..core.db import db

DATA_DIR = Path(__file__).resolve().parent.parent / "data"

def _load_data(filename: str) -> Any:
    path = DATA_DIR / filename
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

# ============================================================================
# 1. RETRIEVAL & LOOKUP TOOLS
# ============================================================================

@tool_registry.register(
    name="get_incident",
    description="Retrieve full incident details, events, and evidence by ID.",
    risk_level="low",
    requires_approval=False,
    category="Incident Management",
    parameter_schema={"incident_id": "string"}
)
def get_incident(incident_id: str) -> Dict[str, Any]:
    inc = db.get_incident_by_id(incident_id)
    if not inc:
        return {"status": "FAILURE", "error": f"Incident {incident_id} not found."}
    return {
        "status": "SUCCESS",
        "incident": inc.model_dump(mode="json")
    }

@tool_registry.register(
    name="get_system_status",
    description="Query live operational status, latency, and health telemetry of corporate infrastructure services.",
    risk_level="low",
    requires_approval=False,
    category="Diagnostics",
    parameter_schema={"service_id": "optional string"}
)
def get_system_status(service_id: Optional[str] = None) -> Dict[str, Any]:
    status_data = _load_data("system_status.json")
    services = status_data.get("services", []) if isinstance(status_data, dict) else []
    if service_id:
        filtered = [s for s in services if s.get("id") == service_id]
        return {"status": "SUCCESS", "services": filtered}
    return {"status": "SUCCESS", "services": services}

@tool_registry.register(
    name="search_knowledge_base",
    description="Search standard operating procedures, known error runbooks, and resolution guides.",
    risk_level="low",
    requires_approval=False,
    category="Knowledge",
    parameter_schema={"query": "string", "category": "optional string"}
)
def search_knowledge_base(query: str, category: Optional[str] = None) -> Dict[str, Any]:
    kb_articles = _load_data("kb_articles.json")
    results = []
    q_lower = query.lower()
    for art in kb_articles:
        score = 0
        if any(tag in q_lower for tag in art.get("tags", [])):
            score += 40
        if q_lower in art.get("title", "").lower() or q_lower in art.get("content", "").lower():
            score += 30
        if category and category.lower() in art.get("category", "").lower():
            score += 30
        if score > 0:
            results.append({**art, "match_score": score})
    results.sort(key=lambda x: x.get("match_score", 0), reverse=True)
    return {"status": "SUCCESS", "articles": results}

@tool_registry.register(
    name="search_past_tickets",
    description="Search resolved historical ITSM incidents to identify recurring root causes and solutions.",
    risk_level="low",
    requires_approval=False,
    category="Knowledge",
    parameter_schema={"query": "string"}
)
def search_past_tickets(query: str) -> Dict[str, Any]:
    tickets = _load_data("past_tickets.json")
    q_lower = query.lower()
    matches = []
    for t in tickets:
        if any(tag in q_lower for tag in t.get("tags", [])) or q_lower in t.get("title", "").lower():
            matches.append(t)
    return {"status": "SUCCESS", "matches": matches}

# ============================================================================
# 2. DIAGNOSTIC TOOLS
# ============================================================================

@tool_registry.register(
    name="check_vpn_diagnostics",
    description="Inspect user gateway session table, handshake state, and token validity on Palo Alto VPN.",
    risk_level="low",
    requires_approval=False,
    category="Diagnostics",
    parameter_schema={"user_id": "string", "gateway": "optional string"}
)
def check_vpn_diagnostics(user_id: str = "usr_current", gateway: str = "gw-us-east") -> Dict[str, Any]:
    return {
        "status": "SUCCESS",
        "gateway": gateway,
        "user_id": user_id,
        "tunnel_state": "DISCONNECTED",
        "stale_session_detected": True,
        "token_status": "EXPIRED",
        "error_code": "AUTH_TOKEN_STALE_SESSION_LOCK",
        "recommended_action": "reset_vpn_session",
        "message": f"Detected expired auth token and stale session lock on {gateway} for {user_id}."
    }

@tool_registry.register(
    name="check_auth_session",
    description="Verify active SSO tokens, SAML assertions, and identity provider session locks.",
    risk_level="low",
    requires_approval=False,
    category="Diagnostics",
    parameter_schema={"user_id": "string", "service": "optional string"}
)
def check_auth_session(user_id: str = "usr_current", service: str = "Okta") -> Dict[str, Any]:
    return {
        "status": "SUCCESS",
        "user_id": user_id,
        "service": service,
        "sso_valid": True,
        "token_lifetime_remaining_sec": 0,
        "session_state": "EXPIRED",
        "message": f"Identity session for {user_id} expired. Needs token cache refresh."
    }

# ============================================================================
# 3. REMEDIATION TOOLS (ALLOWLISTED ACTIONS)
# ============================================================================

@tool_registry.register(
    name="reset_vpn_session",
    description="Clear stale gateway session lock for user and invalidate zombie security associations.",
    risk_level="low",
    requires_approval=False,
    category="Remediation",
    parameter_schema={"user_id": "optional string", "gateway": "optional string"}
)
def reset_vpn_session(user_id: str = "usr_current", gateway: str = "gw-us-east") -> Dict[str, Any]:
    return {
        "status": "SUCCESS",
        "action": "reset_vpn_session",
        "target_user": user_id,
        "gateway": gateway,
        "cleared_sessions": 1,
        "remediation_status": "COMPLETED",
        "message": f"Successfully cleared stale session lock and refreshed token for {user_id} on {gateway}."
    }

@tool_registry.register(
    name="reset_vpn_token",
    description="Alias for reset_vpn_session. Clears stale authentication token on VPN gateway.",
    risk_level="low",
    requires_approval=False,
    category="Remediation",
    parameter_schema={"user_id": "optional string", "gateway": "optional string"}
)
def reset_vpn_token(user_id: str = "usr_current", gateway: str = "gw-us-east") -> Dict[str, Any]:
    return reset_vpn_session(user_id, gateway)

@tool_registry.register(
    name="flush_dns_cache",
    description="Flush local DNS resolver caches and clear corrupted host mappings.",
    risk_level="low",
    requires_approval=False,
    category="Remediation",
    parameter_schema={"scope": "optional string"}
)
def flush_dns_cache(scope: str = "local") -> Dict[str, Any]:
    return {
        "status": "SUCCESS",
        "action": "flush_dns_cache",
        "scope": scope,
        "cleared_entries": 42,
        "remediation_status": "COMPLETED",
        "message": "Successfully purged local DNS resolver cache."
    }

@tool_registry.register(
    name="restart_service",
    description="Restart a local system daemon or container service. Flushes active TCP sockets.",
    risk_level="medium",
    requires_approval=True,
    category="Remediation",
    parameter_schema={"service_name": "string"}
)
def restart_service(service_name: str = "auth_proxy") -> Dict[str, Any]:
    return {
        "status": "SUCCESS",
        "action": "restart_service",
        "service": service_name,
        "new_pid": 19482,
        "remediation_status": "COMPLETED",
        "message": f"Service '{service_name}' successfully restarted with new PID 19482."
    }

@tool_registry.register(
    name="lock_compromised_account",
    description="Emergency revocation of active sessions and OAuth tokens for suspected compromised accounts.",
    risk_level="high",
    requires_approval=True,
    category="Security",
    parameter_schema={"user_id": "string", "reason": "string"}
)
def lock_compromised_account(user_id: str, reason: str = "Suspected unauthorized access") -> Dict[str, Any]:
    return {
        "status": "SUCCESS",
        "action": "lock_compromised_account",
        "user_id": user_id,
        "reason": reason,
        "sessions_terminated": 3,
        "mfa_challenged": True,
        "remediation_status": "LOCKED",
        "message": f"Account '{user_id}' locked pending Security Operations identity verification."
    }

# ============================================================================
# 4. VERIFICATION TOOLS
# ============================================================================

@tool_registry.register(
    name="verify_connectivity",
    description="Perform active health probe, handshake verification, and port check.",
    risk_level="low",
    requires_approval=False,
    category="Verification",
    parameter_schema={"target": "string", "probe_type": "optional string"}
)
def verify_connectivity(target: str = "vpn_gateway", probe_type: str = "handshake") -> Dict[str, Any]:
    return {
        "status": "SUCCESS",
        "verified": True,
        "target": target,
        "probe_type": probe_type,
        "latency_ms": 18,
        "packet_loss_pct": 0,
        "message": f"Active probe to '{target}' succeeded with 0% packet loss and verified health."
    }

@tool_registry.register(
    name="verify_resolution",
    description="Evaluate post-remediation health across network, auth token, and application layers.",
    risk_level="low",
    requires_approval=False,
    category="Verification",
    parameter_schema={"incident_id": "optional string", "action_taken": "optional string"}
)
def verify_resolution(incident_id: Optional[str] = None, action_taken: Optional[str] = None) -> Dict[str, Any]:
    return {
        "status": "SUCCESS",
        "verified": True,
        "incident_id": incident_id,
        "action_verified": action_taken or "system_remediation",
        "latency_ms": 16,
        "healthy": True,
        "message": "Comprehensive post-fix diagnostic probe verified 100% operational state."
    }

# ============================================================================
# 5. TICKETING & ESCALATION TOOLS
# ============================================================================

@tool_registry.register(
    name="create_jira_escalation_ticket",
    description="Create Tier-2 IT support escalation ticket with structured diagnostic brief.",
    risk_level="low",
    requires_approval=False,
    category="Ticketing",
    parameter_schema={"summary": "string", "priority": "optional string", "queue": "optional string", "diagnostic_notes": "optional string"}
)
def create_jira_escalation_ticket(
    summary: str,
    priority: str = "P2",
    queue: str = "Tier2_Support",
    diagnostic_notes: str = ""
) -> Dict[str, Any]:
    ticket_id = f"JIRA-ESCALATE-{int(time.time()) % 10000}"
    return {
        "status": "SUCCESS",
        "ticket_id": ticket_id,
        "queue": queue,
        "priority": priority,
        "summary": summary,
        "diagnostic_notes": diagnostic_notes,
        "message": f"Created escalation ticket {ticket_id} in queue '{queue}'."
    }

@tool_registry.register(
    name="escalate_to_human",
    description="Escalate incident to human engineering team with complete diagnostic summary.",
    risk_level="low",
    requires_approval=False,
    category="Ticketing",
    parameter_schema={"incident_id": "optional string", "reason": "string", "queue": "optional string"}
)
def escalate_to_human(reason: str, incident_id: Optional[str] = None, queue: str = "Tier2_IT_Support") -> Dict[str, Any]:
    ticket_id = f"ITSM-TIER2-{int(time.time()) % 10000}"
    return {
        "status": "SUCCESS",
        "ticket_id": ticket_id,
        "queue": queue,
        "incident_id": incident_id,
        "reason": reason,
        "message": f"Escalated incident to {queue} (Ref: {ticket_id}). Reason: {reason}"
    }

@tool_registry.register(
    name="update_incident_status",
    description="Update operational status and notes on an existing incident.",
    risk_level="low",
    requires_approval=False,
    category="Incident Management",
    parameter_schema={"incident_id": "string", "status": "string", "notes": "optional string"}
)
def update_incident_status(incident_id: str, status: str, notes: Optional[str] = None) -> Dict[str, Any]:
    inc = db.get_incident_by_id(incident_id)
    if inc:
        inc.status = status
        db.save_incident(inc)
        return {"status": "SUCCESS", "incident_id": incident_id, "new_status": status}
    return {"status": "FAILURE", "error": f"Incident {incident_id} not found."}
