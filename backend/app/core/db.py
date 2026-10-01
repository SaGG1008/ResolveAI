import json
import sqlite3
import os
import uuid
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Optional, Dict
from ..models.schemas import (
    Incident,
    AgentEvent,
    Evidence,
    Diagnosis,
    Action,
    IncidentResolution,
    DashboardMetrics
)

DB_PATH = Path(__file__).resolve().parent.parent.parent / "resolveai.db"

class Database:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = str(db_path)
        self._init_db()

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        with self._get_conn() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS incidents (
                    id TEXT PRIMARY KEY,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    status TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    category TEXT NOT NULL,
                    approval_required INTEGER NOT NULL DEFAULT 0,
                    escalation_reason TEXT,
                    diagnosis_json TEXT,
                    action_json TEXT,
                    resolution_json TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS evidence_items (
                    id TEXT NOT NULL,
                    incident_id TEXT NOT NULL,
                    type TEXT NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    relevance INTEGER NOT NULL,
                    source TEXT,
                    PRIMARY KEY (id, incident_id),
                    FOREIGN KEY (incident_id) REFERENCES incidents (id)
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS agent_events (
                    id TEXT NOT NULL,
                    incident_id TEXT NOT NULL,
                    agent TEXT NOT NULL,
                    status TEXT NOT NULL,
                    message TEXT NOT NULL,
                    evidence_json TEXT,
                    diagnosis_json TEXT,
                    action_json TEXT,
                    timestamp TEXT NOT NULL,
                    PRIMARY KEY (id, incident_id),
                    FOREIGN KEY (incident_id) REFERENCES incidents (id)
                )
            """)
            conn.commit()
            
            # Check if seed incidents exist, if not insert initial records
            cursor = conn.execute("SELECT COUNT(*) as count FROM incidents")
            count = cursor.fetchone()["count"]
            if count == 0:
                self._seed_default_incidents(conn)

    def _seed_default_incidents(self, conn: sqlite3.Connection):
        now = datetime.now(timezone.utc).isoformat()
        
        # Scenario 1: Resolved VPN Incident
        inc1_id = "INC-1042"
        inc1_evidence = [
            {"id": "ev-1", "type": "knowledge_base", "title": "KB-104: GlobalProtect VPN Session Reset Procedure", "content": "Stale gateway session locks can be cleared via reset_vpn_session.", "relevance": 95, "source": "Knowledge Base"},
            {"id": "ev-2", "type": "system_status", "title": "VPN Gateway Status (US-East)", "content": "User session usr_9482 flagged as STALE_LOCK.", "relevance": 92, "source": "Palo Alto Telemetry"}
        ]
        inc1_diagnosis = {
            "likelyCause": "Stale session lock on VPN Gateway",
            "confidence": 94,
            "supportingEvidence": inc1_evidence,
            "uncertainty": None
        }
        inc1_action = {
            "id": "act-1",
            "tool": "reset_vpn_session",
            "description": "Clear stale session token and allow fresh authentication.",
            "riskLevel": "low",
            "requiresApproval": False,
            "linkedEvidence": inc1_evidence,
            "reasoning": "Standard zero-blast-radius automated remediation for ghost sessions."
        }
        inc1_res = {
            "timestamp": now,
            "verificationMethod": "Gateway Handshake Probe & Ping Test",
            "success": True
        }
        inc1_events = [
            {
                "id": "evt-101",
                "timestamp": now,
                "agent": "triage",
                "status": "completed",
                "message": "Incident classified as Network / VPN with High priority. Dispatching investigation."
            },
            {
                "id": "evt-102",
                "timestamp": now,
                "agent": "investigation",
                "status": "completed",
                "message": "Retrieved 2 relevant knowledge base articles and verified gateway telemetry.",
                "evidence": inc1_evidence
            },
            {
                "id": "evt-103",
                "timestamp": now,
                "agent": "diagnosis",
                "status": "completed",
                "message": "Diagnosis formulated: Stale session lock on gateway preventing client tunnel handshake.",
                "diagnosis": inc1_diagnosis
            },
            {
                "id": "evt-104",
                "timestamp": now,
                "agent": "action_planner",
                "status": "completed",
                "message": "Selected low-risk tool: reset_vpn_session. Executing remediation.",
                "action": inc1_action
            },
            {
                "id": "evt-105",
                "timestamp": now,
                "agent": "verification",
                "status": "completed",
                "message": "Verification probe confirmed active tunnel handshake and 0% packet loss. Incident resolved."
            }
        ]

        conn.execute("""
            INSERT OR REPLACE INTO incidents (id, title, description, status, priority, category, approval_required, diagnosis_json, action_json, resolution_json, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            inc1_id,
            "VPN Disconnects Every 5 Minutes",
            "User reports VPN drops continuously with Authentication Session Expired alert.",
            "resolved",
            "high",
            "Network / VPN",
            0,
            json.dumps(inc1_diagnosis),
            json.dumps(inc1_action),
            json.dumps(inc1_res),
            now,
            now
        ))

        for ev in inc1_evidence:
            conn.execute("""
                INSERT OR REPLACE INTO evidence_items (id, incident_id, type, title, content, relevance, source)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (ev["id"], inc1_id, ev["type"], ev["title"], ev["content"], ev["relevance"], ev.get("source")))

        for evt in inc1_events:
            conn.execute("""
                INSERT OR REPLACE INTO agent_events (id, incident_id, agent, status, message, evidence_json, diagnosis_json, action_json, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                evt["id"],
                inc1_id,
                evt["agent"],
                evt["status"],
                evt["message"],
                json.dumps(evt.get("evidence")) if evt.get("evidence") else None,
                json.dumps(evt.get("diagnosis")) if evt.get("diagnosis") else None,
                json.dumps(evt.get("action")) if evt.get("action") else None,
                evt["timestamp"]
            ))

        # Scenario 2: Pending Approval Auth Proxy Incident
        inc2_id = "INC-1043"
        inc2_evidence = [
            {"id": "ev-3", "type": "system_status", "title": "Local Auth Proxy Daemon Status", "content": "Process auth_proxy is dead (Exit 137 OOM).", "relevance": 96, "source": "Process Monitor"},
            {"id": "ev-4", "type": "knowledge_base", "title": "KB-318: Engineering Proxy Troubleshooting", "content": "Port 8080 refusal requires restarting the auth_proxy daemon.", "relevance": 88, "source": "Knowledge Base"}
        ]
        inc2_diagnosis = {
            "likelyCause": "Local auth_proxy daemon crashed due to OOM",
            "confidence": 89,
            "supportingEvidence": inc2_evidence,
            "uncertainty": "Requires restart confirmation as active connections may be reset"
        }
        inc2_action = {
            "id": "act-2",
            "tool": "restart_service(auth_proxy)",
            "description": "Restart the local authentication proxy service to reopen port 8080.",
            "riskLevel": "medium",
            "requiresApproval": True,
            "linkedEvidence": inc2_evidence,
            "reasoning": "Restarting a shared background daemon carries medium risk and requires operator approval."
        }
        inc2_events = [
            {
                "id": "evt-201",
                "timestamp": now,
                "agent": "triage",
                "status": "completed",
                "message": "Incident classified as Engineering Tools / Service with Medium priority."
            },
            {
                "id": "evt-202",
                "timestamp": now,
                "agent": "investigation",
                "status": "completed",
                "message": "Identified dead daemon on port 8080 and matching recovery playbook.",
                "evidence": inc2_evidence
            },
            {
                "id": "evt-203",
                "timestamp": now,
                "agent": "diagnosis",
                "status": "completed",
                "message": "Diagnosis formulated: auth_proxy daemon crashed with exit 137.",
                "diagnosis": inc2_diagnosis
            },
            {
                "id": "evt-204",
                "timestamp": now,
                "agent": "action_planner",
                "status": "completed",
                "message": "Planned action restart_service is classified as Medium Risk. Pausing for human approval.",
                "action": inc2_action
            }
        ]

        conn.execute("""
            INSERT OR REPLACE INTO incidents (id, title, description, status, priority, category, approval_required, diagnosis_json, action_json, resolution_json, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            inc2_id,
            "Git Clone Connection Refused (Port 8080)",
            "Cannot pull repos from internal git mirrors, port 8080 connection refused.",
            "pending_approval",
            "medium",
            "Services",
            1,
            json.dumps(inc2_diagnosis),
            json.dumps(inc2_action),
            None,
            now,
            now
        ))

        for ev in inc2_evidence:
            conn.execute("""
                INSERT OR REPLACE INTO evidence_items (id, incident_id, type, title, content, relevance, source)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (ev["id"], inc2_id, ev["type"], ev["title"], ev["content"], ev["relevance"], ev.get("source")))

        for evt in inc2_events:
            conn.execute("""
                INSERT OR REPLACE INTO agent_events (id, incident_id, agent, status, message, evidence_json, diagnosis_json, action_json, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                evt["id"],
                inc2_id,
                evt["agent"],
                evt["status"],
                evt["message"],
                json.dumps(evt.get("evidence")) if evt.get("evidence") else None,
                json.dumps(evt.get("diagnosis")) if evt.get("diagnosis") else None,
                json.dumps(evt.get("action")) if evt.get("action") else None,
                evt["timestamp"]
            ))

        # Scenario 3: Escalated Hardware Kernel Crash
        inc3_id = "INC-1044"
        inc3_evidence = [
            {"id": "ev-5", "type": "knowledge_base", "title": "KB-412: Hardware Memory Parity & Kernel Panics", "content": "Kernel stop code 0x889FA indicates physical memory decay. Automated remediation infeasible.", "relevance": 94, "source": "Hardware Runbook"}
        ]
        inc3_diagnosis = {
            "likelyCause": "Unrecoverable hardware memory parity corruption (Code 0x889FA)",
            "confidence": 35,
            "supportingEvidence": inc3_evidence,
            "uncertainty": "Physical hardware fault detected; cannot be resolved via software tools."
        }
        inc3_events = [
            {
                "id": "evt-301",
                "timestamp": now,
                "agent": "triage",
                "status": "completed",
                "message": "Incident classified as Hardware / Kernel with Critical priority."
            },
            {
                "id": "evt-302",
                "timestamp": now,
                "agent": "investigation",
                "status": "completed",
                "message": "Retrieved hardware failure signature matching unrecoverable memory degradation.",
                "evidence": inc3_evidence
            },
            {
                "id": "evt-303",
                "timestamp": now,
                "agent": "diagnosis",
                "status": "completed",
                "message": "Diagnosis confidence low (35%) for automated remediation. Escalation triggered.",
                "diagnosis": inc3_diagnosis
            },
            {
                "id": "evt-304",
                "timestamp": now,
                "agent": "action_planner",
                "status": "failed",
                "message": "No safe automated tool available. Generating Tier-2 Hardware Provisioning escalation ticket."
            }
        ]

        conn.execute("""
            INSERT OR REPLACE INTO incidents (id, title, description, status, priority, category, approval_required, escalation_reason, diagnosis_json, action_json, resolution_json, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            inc3_id,
            "Screen Flickers Purple then Throws Kernel Panic 0x889FA",
            "Laptop screen started flickering purple then immediately crashed with stop code 0x889FA.",
            "escalated",
            "critical",
            "Hardware",
            0,
            "Physical memory corruption requires immediate Tier-2 Hardware swap.",
            json.dumps(inc3_diagnosis),
            None,
            None,
            now,
            now
        ))

        for ev in inc3_evidence:
            conn.execute("""
                INSERT OR REPLACE INTO evidence_items (id, incident_id, type, title, content, relevance, source)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (ev["id"], inc3_id, ev["type"], ev["title"], ev["content"], ev["relevance"], ev.get("source")))

        for evt in inc3_events:
            conn.execute("""
                INSERT OR REPLACE INTO agent_events (id, incident_id, agent, status, message, evidence_json, diagnosis_json, action_json, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                evt["id"],
                inc3_id,
                evt["agent"],
                evt["status"],
                evt["message"],
                json.dumps(evt.get("evidence")) if evt.get("evidence") else None,
                json.dumps(evt.get("diagnosis")) if evt.get("diagnosis") else None,
                json.dumps(evt.get("action")) if evt.get("action") else None,
                evt["timestamp"]
            ))

        conn.commit()

    def get_all_incidents(self) -> List[Incident]:
        with self._get_conn() as conn:
            cursor = conn.execute("SELECT * FROM incidents ORDER BY created_at DESC")
            rows = cursor.fetchall()
            return [self._row_to_incident(row, conn) for row in rows]

    def get_incident_by_id(self, incident_id: str) -> Optional[Incident]:
        with self._get_conn() as conn:
            cursor = conn.execute("SELECT * FROM incidents WHERE id = ?", (incident_id,))
            row = cursor.fetchone()
            if not row:
                return None
            return self._row_to_incident(row, conn)

    def save_incident(self, incident: Incident):
        with self._get_conn() as conn:
            conn.execute("""
                INSERT INTO incidents (
                    id, title, description, status, priority, category,
                    approval_required, escalation_reason, diagnosis_json,
                    action_json, resolution_json, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    title = excluded.title,
                    description = excluded.description,
                    status = excluded.status,
                    priority = excluded.priority,
                    category = excluded.category,
                    approval_required = excluded.approval_required,
                    escalation_reason = excluded.escalation_reason,
                    diagnosis_json = excluded.diagnosis_json,
                    action_json = excluded.action_json,
                    resolution_json = excluded.resolution_json,
                    updated_at = excluded.updated_at
            """, (
                incident.id,
                incident.title,
                incident.description,
                incident.status,
                incident.priority,
                incident.category,
                1 if incident.approvalRequired else 0,
                incident.escalationReason,
                json.dumps(incident.diagnosis.model_dump(mode="json")) if incident.diagnosis else None,
                json.dumps(incident.proposedAction.model_dump(mode="json")) if incident.proposedAction else None,
                json.dumps(incident.resolution.model_dump(mode="json")) if incident.resolution else None,
                incident.createdAt.isoformat(),
                incident.updatedAt.isoformat()
            ))

            # Replace evidence items for this incident
            conn.execute("DELETE FROM evidence_items WHERE incident_id = ?", (incident.id,))
            for ev in incident.evidence:
                conn.execute("""
                    INSERT OR REPLACE INTO evidence_items (id, incident_id, type, title, content, relevance, source)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (ev.id, incident.id, ev.type, ev.title, ev.content, ev.relevance, ev.source))

            # Replace agent events for this incident
            conn.execute("DELETE FROM agent_events WHERE incident_id = ?", (incident.id,))
            for evt in incident.events:
                conn.execute("""
                    INSERT OR REPLACE INTO agent_events (id, incident_id, agent, status, message, evidence_json, diagnosis_json, action_json, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    evt.id,
                    incident.id,
                    evt.agent,
                    evt.status,
                    evt.message,
                    json.dumps([e.model_dump(mode="json") for e in evt.evidence]) if evt.evidence else None,
                    json.dumps(evt.diagnosis.model_dump(mode="json")) if evt.diagnosis else None,
                    json.dumps(evt.action.model_dump(mode="json")) if evt.action else None,
                    evt.timestamp.isoformat()
                ))
            conn.commit()

    def get_dashboard_metrics(self) -> DashboardMetrics:
        with self._get_conn() as conn:
            total_cursor = conn.execute("SELECT COUNT(*) as count FROM incidents")
            total = total_cursor.fetchone()["count"]

            resolved_cursor = conn.execute("SELECT COUNT(*) as count FROM incidents WHERE status = 'resolved'")
            resolved = resolved_cursor.fetchone()["count"]

            escalated_cursor = conn.execute("SELECT COUNT(*) as count FROM incidents WHERE status = 'escalated'")
            escalated = escalated_cursor.fetchone()["count"]

            active = total - resolved - escalated
            if active < 0:
                active = 0

            return DashboardMetrics(
                activeIncidents=active,
                aiResolutions=resolved,
                escalations=escalated,
                avgResolutionTime=4.2
            )

    def _row_to_incident(self, row: sqlite3.Row, conn: sqlite3.Connection) -> Incident:
        inc_id = row["id"]
        
        # Fetch evidence
        ev_cursor = conn.execute("SELECT * FROM evidence_items WHERE incident_id = ?", (inc_id,))
        evidence = [
            Evidence(
                id=ev_row["id"],
                type=ev_row["type"],
                title=ev_row["title"],
                content=ev_row["content"],
                relevance=ev_row["relevance"],
                source=ev_row["source"]
            )
            for ev_row in ev_cursor.fetchall()
        ]

        # Fetch events
        evt_cursor = conn.execute("SELECT * FROM agent_events WHERE incident_id = ? ORDER BY timestamp ASC", (inc_id,))
        events = []
        for evt_row in evt_cursor.fetchall():
            ev_list = [Evidence(**e) for e in json.loads(evt_row["evidence_json"])] if evt_row["evidence_json"] else None
            diag = Diagnosis(**json.loads(evt_row["diagnosis_json"])) if evt_row["diagnosis_json"] else None
            act = Action(**json.loads(evt_row["action_json"])) if evt_row["action_json"] else None
            
            events.append(AgentEvent(
                id=evt_row["id"],
                timestamp=datetime.fromisoformat(evt_row["timestamp"]),
                agent=evt_row["agent"],
                status=evt_row["status"],
                message=evt_row["message"],
                evidence=ev_list,
                diagnosis=diag,
                action=act
            ))

        diagnosis = Diagnosis(**json.loads(row["diagnosis_json"])) if row["diagnosis_json"] else None
        action = Action(**json.loads(row["action_json"])) if row["action_json"] else None
        resolution = IncidentResolution(**json.loads(row["resolution_json"])) if row["resolution_json"] else None

        return Incident(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            status=row["status"],
            createdAt=datetime.fromisoformat(row["created_at"]),
            updatedAt=datetime.fromisoformat(row["updated_at"]),
            priority=row["priority"],
            category=row["category"],
            events=events,
            evidence=evidence,
            diagnosis=diagnosis,
            proposedAction=action,
            approvalRequired=bool(row["approval_required"]),
            escalationReason=row["escalation_reason"],
            resolution=resolution
        )

# Global DB singleton
db = Database()
