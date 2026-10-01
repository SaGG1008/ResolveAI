# DATABASE — Schema Definition & Persistence Architecture

## ResolveAI — AI IT Service Desk Autonomous Resolution Agent

**Version:** 1.0  
**Engine:** SQLite (File-based storage at `resolveai.db`)  
**ORM:** SQLModel / SQLAlchemy 2.0 with Pydantic v2  

---

## 1. Database Architecture Overview

ResolveAI utilizes an embedded SQLite database optimized for sub-millisecond local reads and writes during incident resolution. The schema is organized into primary transactional entities (`incidents`, `evidence_items`, `agent_traces`, `tool_executions`) and read-only knowledge reference stores (`kb_articles`, `past_tickets`, `system_services`).

```
┌─────────────────────────┐
│        incidents        │
│ id (PK)                 │◀───────────┐
│ title                   │            │
│ status                  │            │
│ category, priority      │            │
└────────────┬────────────┘            │
             │                         │
             ├──▶ (1:N) ┌──────────────┴──────────────┐
             │          │       evidence_items        │
             │          │ id (PK), incident_id (FK)   │
             │          │ source_type, title, snippet │
             │          └─────────────────────────────┘
             │
             ├──▶ (1:N) ┌─────────────────────────────┐
             │          │        agent_traces         │
             │          │ id (PK), incident_id (FK)   │
             │          │ agent_name, step_type, body │
             │          └─────────────────────────────┘
             │
             └──▶ (1:N) ┌─────────────────────────────┐
                        │       tool_executions       │
                        │ id (PK), incident_id (FK)   │
                        │ tool_name, risk, result     │
                        └─────────────────────────────┘
```

---

## 2. Table Schemas & Definitions

### 2.1 Table: `incidents`
Stores core incident records and active lifecycle states.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `VARCHAR(36)` | `PRIMARY KEY` | Unique ID (e.g., `inc_7f8a12bc`) |
| `title` | `VARCHAR(255)` | `NOT NULL` | Short descriptive summary |
| `description` | `TEXT` | `NOT NULL` | Original user issue report |
| `user_id` | `VARCHAR(64)` | `NOT NULL` | Reporting employee ID |
| `user_name` | `VARCHAR(128)`| `NULL` | Employee full name |
| `user_email` | `VARCHAR(128)`| `NULL` | Employee email address |
| `category` | `VARCHAR(64)` | `NULL` | Triage category (e.g. `Network/VPN`) |
| `priority` | `VARCHAR(16)` | `DEFAULT 'P3'`| Priority level (`P1`, `P2`, `P3`, `P4`) |
| `status` | `VARCHAR(32)` | `DEFAULT 'RECEIVED'` | Current state machine status |
| `diagnosis_json` | `TEXT` | `NULL` | JSON blob of root cause & confidence |
| `action_json` | `TEXT` | `NULL` | JSON blob of selected tool & params |
| `verification_json` | `TEXT` | `NULL` | JSON blob of verification probe output |
| `resolution_notes` | `TEXT` | `NULL` | Final outcome / handover summary |
| `created_at` | `DATETIME` | `NOT NULL` | Timestamp of intake (UTC) |
| `updated_at` | `DATETIME` | `NOT NULL` | Timestamp of last modification |

---

### 2.2 Table: `evidence_items`
Stores granular facts gathered during the investigation phase.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `VARCHAR(36)` | `PRIMARY KEY` | Unique ID (e.g., `ev_101`) |
| `incident_id` | `VARCHAR(36)` | `FOREIGN KEY (incidents.id)` | Associated incident |
| `source_type` | `VARCHAR(32)` | `NOT NULL` | `KNOWLEDGE_BASE`, `TELEMETRY`, `PAST_TICKETS`, `PROCEDURE` |
| `title` | `VARCHAR(255)` | `NOT NULL` | Human-readable document/source title |
| `snippet` | `TEXT` | `NOT NULL` | Key extracted sentence or log record |
| `relevance_score` | `FLOAT` | `NOT NULL` | Similarity/relevance score ($0.0 - 1.0$) |
| `metadata_json` | `TEXT` | `NULL` | Additional source metadata (URL, ticket ID) |
| `created_at` | `DATETIME` | `NOT NULL` | Discovery timestamp |

---

### 2.3 Table: `agent_traces`
Records step-by-step agent reasoning, tool calls, and state transitions for live UI streaming and audit logs.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `VARCHAR(36)` | `PRIMARY KEY` | Unique ID (e.g., `tr_01`) |
| `incident_id` | `VARCHAR(36)` | `FOREIGN KEY (incidents.id)` | Associated incident |
| `agent_name` | `VARCHAR(64)` | `NOT NULL` | `TriageAgent`, `InvestigationAgent`, etc. |
| `step_type` | `VARCHAR(32)` | `NOT NULL` | `THOUGHT`, `TOOL_CALL`, `DECISION`, `STATE_CHANGE` |
| `content` | `TEXT` | `NOT NULL` | Reasoning explanation or output |
| `status` | `VARCHAR(32)` | `DEFAULT 'COMPLETED'` | `IN_PROGRESS`, `COMPLETED`, `FAILED` |
| `timestamp` | `DATETIME` | `NOT NULL` | Event timestamp |

---

### 2.4 Table: `tool_executions`
Audit record of every remediation tool attempted or executed.

| Column | Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `VARCHAR(36)` | `PRIMARY KEY` | Execution ID |
| `incident_id` | `VARCHAR(36)` | `FOREIGN KEY (incidents.id)` | Associated incident |
| `tool_name` | `VARCHAR(64)` | `NOT NULL` | Target tool identifier |
| `parameters_json` | `TEXT` | `NOT NULL` | Arguments supplied to tool |
| `risk_level` | `VARCHAR(16)` | `NOT NULL` | `LOW`, `MEDIUM`, `HIGH` |
| `requires_approval` | `BOOLEAN` | `NOT NULL` | True if human sign-off needed |
| `approved_by` | `VARCHAR(64)` | `NULL` | Operator ID if approved |
| `execution_status` | `VARCHAR(32)` | `NOT NULL` | `PENDING`, `SUCCESS`, `FAILED`, `REJECTED` |
| `result_json` | `TEXT` | `NULL` | Execution output payload |
| `executed_at` | `DATETIME` | `NOT NULL` | Execution timestamp |

---

## 3. Seed Datasets (Scenario Data)

### 3.1 Scenario 1: VPN Session Lock
* **KB Article:** `KB-104: Troubleshooting GlobalProtect VPN Stale Session Locks`
* **Telemetry:** `gw-vpn-us-east: usr_9482 session status = ZOMBIE_LOCK (Idle: 412 min)`
* **Tool:** `reset_vpn_session(user_id="usr_9482")`
* **Verification:** `probe_vpn_handshake(user_id="usr_9482")` $\rightarrow$ `HTTP 200 SUCCESS`

### 3.2 Scenario 2: Auth Proxy Daemon Crash (Approval Gate)
* **KB Article:** `KB-318: Internal Engineering Mirror Proxy Troubleshooting`
* **Telemetry:** `service_status(name="auth_proxy") = CRASHED (Exit 137)`
* **Tool:** `restart_service(service_name="auth_proxy")` (Risk: `MEDIUM`, Requires Approval: `True`)
* **Verification:** `check_service_port(host="localhost", port=8080)` $\rightarrow$ `PORT_OPEN`

### 3.3 Scenario 3: Hardware / Kernel Fault (Escalation)
* **KB Article:** No high-relevance match ($< 0.40$ relevance)
* **Telemetry:** `sys_diagnostics = MEMORY_PARITY_ERROR (Kernel Panic 0x889FA)`
* **Tool:** `create_jira_escalation_ticket(queue="Tier2_Hardware", priority="P2")`
* **Outcome:** Escalated to human operator with attached crash dump snippet.

---

## 4. Indexing & Optimization
* **`idx_incidents_status`** on `incidents(status)`: Accelerates dashboard status filtering.
* **`idx_evidence_incident_id`** on `evidence_items(incident_id)`: Speeds up evidence retrieval.
* **`idx_traces_incident_id`** on `agent_traces(incident_id, timestamp)`: Guarantees chronologically sorted SSE streaming.
