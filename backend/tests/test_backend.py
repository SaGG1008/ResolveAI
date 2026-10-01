import unittest
import asyncio
import os
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Add backend to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from backend.app.main import app
from backend.app.models.schemas import Incident, Evidence, Diagnosis, Action
from backend.app.core.db import db
from backend.app.tools.registry import tool_registry
from backend.app.agents.triage import triage_agent
from backend.app.agents.investigation import investigation_agent
from backend.app.agents.diagnosis import diagnosis_agent
from backend.app.agents.action_planner import action_planner_agent
from backend.app.agents.verification import verification_agent
from backend.app.agents.orchestrator import orchestrator

class TestResolveAIBackend(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    def test_01_tool_registry(self):
        tools = tool_registry.list_tools()
        self.assertIn("reset_vpn_session", tools)
        self.assertIn("flush_dns_cache", tools)
        self.assertIn("restart_service", tools)
        self.assertIn("create_jira_escalation_ticket", tools)
        self.assertIn("verify_connectivity", tools)

        # Execute low risk tool
        res = tool_registry.execute("reset_vpn_session", user_id="test_user")
        self.assertEqual(res["status"], "SUCCESS")

    def test_02_database_seeded_incidents(self):
        incidents = db.get_all_incidents()
        self.assertGreaterEqual(len(incidents), 3)

        # Check INC-1042 (Resolved VPN)
        inc1 = db.get_incident_by_id("INC-1042")
        self.assertIsNotNone(inc1)
        self.assertEqual(inc1.status, "resolved")
        self.assertGreater(len(inc1.events), 0)
        self.assertGreater(len(inc1.evidence), 0)

        # Check INC-1043 (Pending Approval Proxy)
        inc2 = db.get_incident_by_id("INC-1043")
        self.assertIsNotNone(inc2)
        self.assertEqual(inc2.status, "pending_approval")
        self.assertTrue(inc2.approvalRequired)

        # Check INC-1044 (Escalated Hardware)
        inc3 = db.get_incident_by_id("INC-1044")
        self.assertIsNotNone(inc3)
        self.assertEqual(inc3.status, "escalated")

    def test_03_scenario1_vpn_auto_resolution(self):
        async def run_scenario():
            inc = Incident(
                id="TEST-VPN-01",
                title="VPN Disconnects frequently",
                description="My VPN keeps disconnecting every 5 minutes with session expired message.",
                status="open"
            )
            db.save_incident(inc)

            # Run pipeline
            await orchestrator.run_investigation_pipeline("TEST-VPN-01")

            updated = db.get_incident_by_id("TEST-VPN-01")
            self.assertIsNotNone(updated)
            self.assertEqual(updated.status, "resolved")
            self.assertEqual(updated.category, "Network / VPN")
            self.assertIsNotNone(updated.diagnosis)
            self.assertGreaterEqual(updated.diagnosis.confidence, 90)
            self.assertIsNotNone(updated.resolution)
            self.assertTrue(updated.resolution.success)

        asyncio.run(run_scenario())

    def test_04_scenario2_auth_proxy_approval_gate(self):
        async def run_scenario():
            inc = Incident(
                id="TEST-PROXY-02",
                title="Git Mirror Port 8080 Down",
                description="Cannot reach internal git repo; port 8080 connection refused on auth proxy.",
                status="open"
            )
            db.save_incident(inc)

            await orchestrator.run_investigation_pipeline("TEST-PROXY-02")

            pending = db.get_incident_by_id("TEST-PROXY-02")
            self.assertIsNotNone(pending)
            self.assertEqual(pending.status, "pending_approval")
            self.assertTrue(pending.approvalRequired)
            self.assertEqual(pending.proposedAction.riskLevel, "medium")

            # Simulate Operator Approval
            await orchestrator.execute_and_verify(pending)

            resolved = db.get_incident_by_id("TEST-PROXY-02")
            self.assertEqual(resolved.status, "resolved")
            self.assertFalse(resolved.approvalRequired)

        asyncio.run(run_scenario())

    def test_05_scenario3_hardware_escalation(self):
        async def run_scenario():
            inc = Incident(
                id="TEST-HW-03",
                title="Purple Screen and Kernel Panic",
                description="Laptop screen flickered purple then threw kernel error 0x889FA.",
                status="open"
            )
            db.save_incident(inc)

            await orchestrator.run_investigation_pipeline("TEST-HW-03")

            escalated = db.get_incident_by_id("TEST-HW-03")
            self.assertIsNotNone(escalated)
            self.assertEqual(escalated.status, "escalated")
            self.assertIsNotNone(escalated.escalationReason)

        asyncio.run(run_scenario())

    def test_06_dashboard_metrics(self):
        metrics = db.get_dashboard_metrics()
        self.assertGreaterEqual(metrics.aiResolutions, 1)
        self.assertGreaterEqual(metrics.escalations, 1)

    def test_07_fastapi_rest_endpoints(self):
        # 1. Root
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json()["status"], "OPERATIONAL")

        # 2. List Incidents
        res = self.client.get("/api/incidents")
        self.assertEqual(res.status_code, 200)
        incidents = res.json()
        self.assertIsInstance(incidents, list)
        self.assertGreaterEqual(len(incidents), 3)

        # 3. Get Single Incident
        res = self.client.get("/api/incidents/INC-1042")
        self.assertEqual(res.status_code, 200)
        inc = res.json()
        self.assertEqual(inc["id"], "INC-1042")
        self.assertIn("events", inc)
        self.assertIn("evidence", inc)

        # 4. Create Incident via API
        res = self.client.post("/api/incidents", json={
            "description": "User cannot connect to internal DNS server"
        })
        self.assertEqual(res.status_code, 201)
        created = res.json()
        self.assertTrue(created["id"].startswith("INC-"))

        # 5. Dashboard Metrics API
        res = self.client.get("/api/dashboard/metrics")
        self.assertEqual(res.status_code, 200)
        metrics = res.json()
        self.assertIn("activeIncidents", metrics)
        self.assertIn("aiResolutions", metrics)

        # 6. System Status API
        res = self.client.get("/api/system/status")
        self.assertEqual(res.status_code, 200)
        system_status = res.json()
        self.assertEqual(system_status["status"], "HEALTHY")
        self.assertIn("registered_tools", system_status)

    def test_08_scenario_security_escalation(self):
        """Test secondary escalation scenario: Unauthorized Account Access / Security Incident."""
        async def run_security_scenario():
            inc = Incident(
                id="TEST-SEC-01",
                title="Suspicious account activity",
                description="Someone may have accessed my account from an unfamiliar location.",
                status="open"
            )
            db.save_incident(inc)

            await orchestrator.run_investigation_pipeline("TEST-SEC-01")

            sec_inc = db.get_incident_by_id("TEST-SEC-01")
            self.assertIsNotNone(sec_inc)
            self.assertEqual(sec_inc.category, "Security")
            self.assertEqual(sec_inc.priority, "critical")
            self.assertEqual(sec_inc.status, "pending_approval")
            self.assertTrue(sec_inc.approvalRequired)
            self.assertEqual(sec_inc.proposedAction.riskLevel, "high")
            self.assertGreaterEqual(len(sec_inc.evidence), 1)

            # Operator approval execution
            await orchestrator.execute_and_verify(sec_inc)
            resolved_sec = db.get_incident_by_id("TEST-SEC-01")
            self.assertEqual(resolved_sec.status, "resolved")
            self.assertTrue(resolved_sec.resolution.success)

        asyncio.run(run_security_scenario())

    def test_09_failed_verification_escalation(self):
        """Test that failed verification does NOT claim success and escalates to Tier-2."""
        async def run_fail_verify():
            inc = Incident(
                id="TEST-FAIL-01",
                title="Stubborn VPN Session",
                description="My VPN keeps disconnecting continuously.",
                status="open"
            )
            db.save_incident(inc)

            await orchestrator.run_investigation_pipeline("TEST-FAIL-01")

            inc_obj = db.get_incident_by_id("TEST-FAIL-01")
            # Force verification failure to test escalation path
            await orchestrator.execute_and_verify(inc_obj, simulate_failure=True)

            failed_inc = db.get_incident_by_id("TEST-FAIL-01")
            self.assertEqual(failed_inc.status, "escalated")
            self.assertIsNotNone(failed_inc.escalation)
            self.assertIn("failed", failed_inc.escalationReason.lower())

        asyncio.run(run_fail_verify())

    def test_10_tools_rest_endpoints(self):
        """Test the dedicated /api/tools endpoints."""
        # 1. List tools
        res = self.client.get("/api/tools")
        self.assertEqual(res.status_code, 200)
        tools = res.json()
        self.assertIn("reset_vpn_session", tools)
        self.assertIn("get_system_status", tools)
        self.assertIn("search_knowledge_base", tools)

        # 2. Tools by category
        res = self.client.get("/api/tools/by-category")
        self.assertEqual(res.status_code, 200)
        by_cat = res.json()
        self.assertIn("Diagnostics", by_cat)
        self.assertIn("Remediation", by_cat)

        # 3. Tool execution API
        res = self.client.post("/api/tools/execute", json={
            "name": "check_vpn_diagnostics",
            "parameters": {"user_id": "usr_test"}
        })
        self.assertEqual(res.status_code, 200)
        exec_res = res.json()
        self.assertTrue(exec_res["success"])
        self.assertEqual(exec_res["tool"], "check_vpn_diagnostics")

    def test_11_all_registered_tools_suite(self):
        """Verify deterministic execution across all required tools."""
        # Diagnostic & Lookup
        self.assertEqual(tool_registry.execute("get_system_status")["status"], "SUCCESS")
        self.assertEqual(tool_registry.execute("check_vpn_diagnostics")["status"], "SUCCESS")
        self.assertEqual(tool_registry.execute("check_auth_session")["status"], "SUCCESS")
        self.assertEqual(tool_registry.execute("search_knowledge_base", query="vpn")["status"], "SUCCESS")
        self.assertEqual(tool_registry.execute("search_past_tickets", query="vpn")["status"], "SUCCESS")

        # Remediation
        self.assertEqual(tool_registry.execute("reset_vpn_session")["status"], "SUCCESS")
        self.assertEqual(tool_registry.execute("reset_vpn_token")["status"], "SUCCESS")
        self.assertEqual(tool_registry.execute("flush_dns_cache")["status"], "SUCCESS")
        self.assertEqual(tool_registry.execute("restart_service", service_name="auth_proxy")["status"], "SUCCESS")
        self.assertEqual(tool_registry.execute("lock_compromised_account", user_id="usr_01", reason="test")["status"], "SUCCESS")

        # Verification & Ticketing
        self.assertEqual(tool_registry.execute("verify_connectivity")["status"], "SUCCESS")
        self.assertEqual(tool_registry.execute("verify_resolution")["status"], "SUCCESS")
        self.assertEqual(tool_registry.execute("create_jira_escalation_ticket", summary="test")["status"], "SUCCESS")
        self.assertEqual(tool_registry.execute("escalate_to_human", reason="test")["status"], "SUCCESS")

if __name__ == "__main__":
    unittest.main()

