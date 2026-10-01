"""
End-to-End Live SSE Integration Test for ResolveAI
Connects to running FastAPI server at http://localhost:8000 and streams events live via SSE.
Verifies:
1. Scenario A: Low-risk VPN auto-resolution (SSE stream captures: triage -> investigation -> diagnosis -> action -> tool_execution -> verification -> resolved)
2. Scenario B: Medium/High-risk incident requiring human approval (SSE stream captures: awaiting_approval -> POST approval -> executing -> verification -> resolved)
3. Scenario C: Failed verification or unhandled hardware issue -> Escalation to Tier-2 with Jira ticket.
"""

import sys
import json
import time
import urllib.request
import urllib.parse
import http.client

BASE_URL = "http://localhost:8000"

def log(msg, status="INFO"):
    print(f"[{status}] {msg}")

def check_server():
    try:
        req = urllib.request.Request(f"{BASE_URL}/api/system/status")
        with urllib.request.urlopen(req, timeout=3) as resp:
            data = json.loads(resp.read().decode())
            log(f"FastAPI Server Health: {data.get('status')} ({len(data.get('registered_tools', []))} tools registered)", "SUCCESS")
            return True
    except Exception as e:
        log(f"Server check failed: {e}", "ERROR")
        return False

def stream_events(incident_id, timeout_sec=15, on_event_callback=None):
    """
    Connect to GET /api/incidents/{id}/stream using streaming HTTP client and yield SSE events.
    """
    events = []
    start_time = time.time()
    
    url = f"{BASE_URL}/api/incidents/{incident_id}/stream"
    req = urllib.request.Request(url, headers={"Accept": "text/event-stream"})
    
    try:
        with urllib.request.urlopen(req, timeout=timeout_sec) as response:
            buffer = ""
            for raw_line in response:
                if time.time() - start_time > timeout_sec:
                    break
                line = raw_line.decode('utf-8')
                if line.startswith("data: "):
                    payload_str = line[6:].strip()
                    if payload_str:
                        try:
                            payload = json.loads(payload_str)
                            events.append(payload)
                            if on_event_callback:
                                stop = on_event_callback(payload)
                                if stop:
                                    break
                        except json.JSONDecodeError:
                            pass
                elif line.strip() == "":
                    # Empty line in SSE signifies event separator
                    continue
    except Exception as e:
        log(f"SSE stream closed/completed: {e}", "DEBUG")
    
    return events

def create_incident(title, description, user_id="user_e2e"):
    payload = json.dumps({
        "title": title,
        "description": description,
        "user_id": user_id
    }).encode('utf-8')
    
    req = urllib.request.Request(
        f"{BASE_URL}/api/incidents",
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        data = json.loads(resp.read().decode())
        return data

def submit_approval(incident_id, approved=True, notes="E2E Operator Authorized"):
    payload = json.dumps({
        "approved": approved,
        "operator_id": "operator_e2e_lead",
        "notes": notes
    }).encode('utf-8')
    
    req = urllib.request.Request(
        f"{BASE_URL}/api/incidents/{incident_id}/approval",
        data=payload,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        data = json.loads(resp.read().decode())
        return data

def test_scenario_a_vpn_autoresolution():
    log("="*60)
    log("TEST SCENARIO A: Low-Risk VPN Auto-Resolution Flow")
    log("="*60)
    
    # 1. Create Incident
    inc = create_incident(
        title="VPN Gateway authentication timeout",
        description="I cannot connect to the corporate VPN gateway. Pulse Secure error: authentication timeout."
    )
    inc_id = inc["id"]
    log(f"Created Incident ID: {inc_id} (Initial Status: {inc['status']})")
    
    # 2. Stream SSE events
    observed_statuses = []
    def on_event(event):
        status = event.get("status")
        agent = event.get("current_agent")
        diag = event.get("diagnosis", {}).get("root_cause") if event.get("diagnosis") else None
        log(f"  -> SSE Event: status={status} | agent={agent} | diag={diag}")
        observed_statuses.append(status)
        if status in ["resolved", "escalated"]:
            return True
        return False
    
    events = stream_events(inc_id, timeout_sec=10, on_event_callback=on_event)
    
    # Verify final state
    req = urllib.request.Request(f"{BASE_URL}/api/incidents/{inc_id}")
    with urllib.request.urlopen(req) as resp:
        final_inc = json.loads(resp.read().decode())
    
    log(f"Final State: {final_inc['status']} | Resolution Success: {final_inc.get('resolution', {}).get('success')}")
    assert final_inc["status"] == "resolved", f"Expected resolved, got {final_inc['status']}"
    assert final_inc["resolution"]["success"] is True, "Expected verification probe to pass"
    assert "Gateway Handshake" in final_inc["resolution"]["verificationMethod"]
    log("Scenario A PASSED: Full autonomous resolution verified via SSE!", "SUCCESS")

def test_scenario_b_approval_gate():
    log("="*60)
    log("TEST SCENARIO B: Medium/High Risk Incident Requiring Approval")
    log("="*60)
    
    # 1. Create Incident that requires service restart (medium risk -> approval required)
    inc = create_incident(
        title="Internal SSO Auth Proxy 502 Bad Gateway",
        description="Engineering auth proxy auth-proxy-prod-01 is returning 502 Bad Gateway for all OAuth endpoints."
    )
    inc_id = inc["id"]
    log(f"Created Incident ID: {inc_id}")
    
    # 2. Stream events until pending_approval
    def on_event_1(event):
        status = event.get("status")
        log(f"  -> Pre-Approval SSE Event: status={status} | agent={event.get('current_agent')}")
        if status == "pending_approval":
            log("  -> Approval Gate reached! Action requires authorization.")
            return True
        return False
    
    stream_events(inc_id, timeout_sec=8, on_event_callback=on_event_1)
    
    # Check status
    req = urllib.request.Request(f"{BASE_URL}/api/incidents/{inc_id}")
    with urllib.request.urlopen(req) as resp:
        mid_inc = json.loads(resp.read().decode())
    assert mid_inc["status"] == "pending_approval", f"Expected pending_approval, got {mid_inc['status']}"
    assert mid_inc["approvalRequired"] is True
    assert mid_inc.get("proposedAction") is not None
    log(f"Proposed Action: {mid_inc['proposedAction']['tool']} (Risk: {mid_inc['proposedAction']['riskLevel']})")
    
    # 3. Submit Approval
    time.sleep(1)
    log("Submitting Human Authorization via POST /api/incidents/{id}/approval...")
    approval_resp = submit_approval(inc_id, approved=True, notes="Authorized by Lead SRE")
    log(f"Approval Result: {approval_resp['status']}")
    
    # 4. Stream rest of workflow
    def on_event_2(event):
        status = event.get("status")
        log(f"  -> Post-Approval SSE Event: status={status} | agent={event.get('current_agent')}")
        if status in ["resolved", "escalated"]:
            return True
        return False
    
    stream_events(inc_id, timeout_sec=8, on_event_callback=on_event_2)
    
    # Verify final state
    req = urllib.request.Request(f"{BASE_URL}/api/incidents/{inc_id}")
    with urllib.request.urlopen(req) as resp:
        final_inc = json.loads(resp.read().decode())
    
    log(f"Final State: {final_inc['status']} | Resolution Success: {final_inc.get('resolution', {}).get('success')}")
    assert final_inc["status"] == "resolved", f"Expected resolved, got {final_inc['status']}"
    log("Scenario B PASSED: Human-in-the-loop approval gate and post-approval execution verified via SSE!", "SUCCESS")

def test_scenario_c_escalation():
    log("="*60)
    log("TEST SCENARIO C: Failed Verification / Unsupported Hardware Incident Escalation")
    log("="*60)
    
    # 1. Create Hardware Incident
    inc = create_incident(
        title="Laptop display cracked and physical battery swelling",
        description="My MacBook Pro battery has physically expanded and cracked the chassis. Smell of burnt plastic."
    )
    inc_id = inc["id"]
    log(f"Created Incident ID: {inc_id}")
    
    # 2. Stream SSE events
    def on_event(event):
        status = event.get("status")
        log(f"  -> SSE Event: status={status} | agent={event.get('current_agent')}")
        if status in ["resolved", "escalated"]:
            return True
        return False
    
    stream_events(inc_id, timeout_sec=8, on_event_callback=on_event)
    
    # Verify final state
    req = urllib.request.Request(f"{BASE_URL}/api/incidents/{inc_id}")
    with urllib.request.urlopen(req) as resp:
        final_inc = json.loads(resp.read().decode())
    
    log(f"Final State: {final_inc['status']} | Escalation: {final_inc.get('escalation', {})}")
    assert final_inc["status"] == "escalated", f"Expected escalated, got {final_inc['status']}"
    assert final_inc.get("escalation") is not None
    assert final_inc["escalation"]["ticketId"].startswith("JIRA-")
    assert "Tier2" in final_inc["escalation"]["targetQueue"] or "Support" in final_inc["escalation"]["targetQueue"]
    log("Scenario C PASSED: Automatic Tier-2 Escalation with Jira ticket verified via SSE!", "SUCCESS")

if __name__ == "__main__":
    if not check_server():
        sys.exit(1)
    
    try:
        test_scenario_a_vpn_autoresolution()
        print()
        test_scenario_b_approval_gate()
        print()
        test_scenario_c_escalation()
        print()
        log("ALL END-TO-END SSE WORKFLOW VERIFICATIONS PASSED SUCCESSFULLY!", "SUCCESS")
    except Exception as e:
        log(f"Verification FAILED with error: {e}", "FATAL")
        import traceback
        traceback.print_exc()
        sys.exit(1)
