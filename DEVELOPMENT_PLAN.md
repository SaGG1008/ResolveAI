# DEVELOPMENT_PLAN — Engineering Roadmap & Phase Breakdown

## ResolveAI — AI IT Service Desk Autonomous Resolution Agent

**Version:** 1.0  
**Target:** Hackathon MVP (3.5 Hours Delivery Schedule)  
**Execution Strategy:** Parallel frontend UI development (Claude workstream) alongside backend architecture, database modeling, and agent orchestrator implementation (Antigravity workstream).

---

## Priority Classifications
* **P0:** Mandatory for core demo scenarios and MVP completion.
* **P1:** Important for production polish, reliability, and error resilience.
* **P2:** Useful quality-of-life enhancements.
* **P3:** Post-hackathon future capabilities.

---

## Phase 1: Frontend UI Implementation (Claude Workstream)

### Task 1.1: Frontend Design Tokens & Component Layout Frame
* **Purpose:** Establish topbar, sidebar, theme toggling, and main content area container.
* **Files Affected:** `frontend/src/components/layout/`, `frontend/src/index.css`, `frontend/src/App.tsx`
* **Dependencies:** None
* **Priority:** P0
* **Completion Criteria:** Responsive layout frame renders cleanly with navigation tabs.

### Task 1.2: Dashboard View & Quick-Intake Bar
* **Purpose:** Display high-level KPI cards, recent incident table, and natural-language issue submission box.
* **Files Affected:** `frontend/src/components/dashboard/`, `frontend/src/types/incident.ts`
* **Dependencies:** Task 1.1
* **Priority:** P0
* **Completion Criteria:** User can type an issue and click "Investigate" to trigger the incident flow.

### Task 1.3: Incident Workspace & Live Agent Activity Trace
* **Purpose:** Two-column workspace showing real-time agent thoughts, tool calls, and state progression.
* **Files Affected:** `frontend/src/components/agent/`, `frontend/src/components/incident/`
* **Dependencies:** Task 1.2
* **Priority:** P0
* **Completion Criteria:** Agent timeline renders step-by-step progress with animated indicators for active steps.

### Task 1.4: Grounded Evidence Drawer & Diagnostics Card
* **Purpose:** Render evidence cards showing KB snippets, telemetry logs, and past ticket matches with confidence scores.
* **Files Affected:** `frontend/src/components/evidence/`
* **Dependencies:** Task 1.3
* **Priority:** P0
* **Completion Criteria:** Users can click evidence items to expand source details and relevance scores.

### Task 1.5: Human Approval Modal & Risk Indicator
* **Purpose:** Interactive dialog prompting the user/admin to approve or reject elevated actions.
* **Files Affected:** `frontend/src/components/common/ApprovalModal.tsx`
* **Dependencies:** Task 1.3
* **Priority:** P0
* **Completion Criteria:** Modal appears during `AWAITING_APPROVAL`, allowing single-click execution or rejection.

---

## Phase 2: Backend Architecture & REST API (Antigravity Workstream)

### Task 2.1: FastAPI Server Setup & Project Structure
* **Purpose:** Initialize FastAPI backend with CORS middleware, configuration loaders, and error handlers.
* **Files Affected:** `backend/app/main.py`, `backend/app/config.py`, `backend/requirements.txt`
* **Dependencies:** None
* **Priority:** P0
* **Completion Criteria:** Server boots on `http://localhost:8000/docs` with clean OpenAPI docs.

### Task 2.2: Incident & State Management Endpoints
* **Purpose:** Endpoints for incident creation (`POST /api/incidents`), lookup (`GET /api/incidents/{id}`), and listing (`GET /api/incidents`).
* **Files Affected:** `backend/app/api/incidents.py`, `backend/app/models/incident.py`
* **Dependencies:** Task 2.1
* **Priority:** P0
* **Completion Criteria:** Successfully create and retrieve incidents with full type validation.

### Task 2.3: Real-Time Event Stream (SSE)
* **Purpose:** Stream agent trace events and status changes to frontend clients in real time.
* **Files Affected:** `backend/app/api/agent_events.py`, `backend/app/core/state_machine.py`
* **Dependencies:** Task 2.2
* **Priority:** P0
* **Completion Criteria:** Client receives real-time JSON stream updates as incident state changes.

---

## Phase 3: Database & Persistence Layer

### Task 3.1: Database Models & SQLite Schema
* **Purpose:** Define SQLModel / SQLAlchemy entities for `incidents`, `evidence_items`, `agent_traces`, and `tool_executions`.
* **Files Affected:** `backend/app/models/`, `backend/app/core/db.py`
* **Dependencies:** Task 2.1
* **Priority:** P0
* **Completion Criteria:** Database automatically creates tables on startup and persists incident history.

### Task 3.2: Seed Datasets for Knowledge Base & Service Telemetry
* **Purpose:** Populate realistic KB articles, past tickets, and system health status JSON files for the 3 demo scenarios.
* **Files Affected:** `backend/app/data/kb_articles.json`, `backend/app/data/past_tickets.json`, `backend/app/data/system_status.json`
* **Dependencies:** Task 3.1
* **Priority:** P0
* **Completion Criteria:** Structured mock data available for instant querying by the investigation agent.

---

## Phase 4: Multi-Agent Runtime & Tool Registry

### Task 4.1: Controlled Tool Registry & Handlers
* **Purpose:** Implement safe Python remediation tools (`reset_vpn_session`, `flush_dns_cache`, `restart_service`, etc.) with risk tagging.
* **Files Affected:** `backend/app/tools/registry.py`, `backend/app/tools/handlers.py`
* **Dependencies:** Task 2.1
* **Priority:** P0
* **Completion Criteria:** Tools execute safely and return structured JSON output with error handling.

### Task 4.2: Triage & Investigation (RAG) Agents
* **Purpose:** Classify issue, query KB/telemetry seed files, and attach structured evidence items.
* **Files Affected:** `backend/app/agents/triage.py`, `backend/app/agents/investigation.py`
* **Dependencies:** Tasks 3.2, 4.1
* **Priority:** P0
* **Completion Criteria:** Issue is categorized and supported by at least 2 relevant evidence items.

### Task 4.3: Diagnosis & Action Planner Agents
* **Purpose:** Synthesize root causes, assign risk levels, and choose allowlisted remediation tools.
* **Files Affected:** `backend/app/agents/diagnosis.py`, `backend/app/agents/action_planner.py`
* **Dependencies:** Task 4.2
* **Priority:** P0
* **Completion Criteria:** Planner selects appropriate tool or halts for approval if risk is elevated.

### Task 4.4: Verification & Escalation Agents
* **Purpose:** Execute active post-remediation health probes and compile handover briefs for failed/ambiguous cases.
* **Files Affected:** `backend/app/agents/verification.py`, `backend/app/agents/escalation.py`
* **Dependencies:** Task 4.3
* **Priority:** P0
* **Completion Criteria:** Incidents verify successfully before `RESOLVED` or transition to `ESCALATED`.

---

## Phase 5: API & Frontend Integration

### Task 5.1: Frontend API Service & SSE Hook
* **Purpose:** Connect React UI to FastAPI backend via `fetch` and `EventSource` subscriptions.
* **Files Affected:** `frontend/src/services/api.ts`, `frontend/src/hooks/useIncidentStream.ts`
* **Dependencies:** Tasks 1.3, 2.3
* **Priority:** P0
* **Completion Criteria:** Frontend updates live as the backend agent orchestrator executes.

### Task 5.2: Human Approval Action Wire-up
* **Purpose:** Connect approval modal CTA to `POST /api/incidents/{id}/approval`.
* **Files Affected:** `frontend/src/components/common/ApprovalModal.tsx`, `backend/app/api/approvals.py`
* **Dependencies:** Tasks 1.5, 5.1
* **Priority:** P0
* **Completion Criteria:** Clicking "Approve" resumes agent execution to perform the remediation.

---

## Phase 6: Testing & Quality Assurance

### Task 6.1: End-to-End Scenario Verification Suite
* **Purpose:** Validate all 3 demo flows (VPN auto-resolution, proxy restart approval, and hardware escalation) execute cleanly.
* **Files Affected:** `backend/tests/test_scenarios.py`
* **Dependencies:** Phase 5
* **Priority:** P0
* **Completion Criteria:** 100% pass rate on core scenario test runs.

### Task 6.2: Frontend Build & Lint Verification
* **Purpose:** Ensure zero TypeScript errors and successful production bundling.
* **Files Affected:** `frontend/`
* **Dependencies:** Phase 5
* **Priority:** P0
* **Completion Criteria:** `npm run build` and `npm run lint` pass without errors.

---

## Phase 7: Security & Guardrails

### Task 7.1: Input Sanitization & Parameter Validation
* **Purpose:** Enforce length boundaries and prevent injection in issue descriptions and tool payloads.
* **Files Affected:** `backend/app/core/security.py`
* **Dependencies:** Phase 2
* **Priority:** P1
* **Completion Criteria:** Malformed or excessively long inputs are rejected with descriptive 400 responses.

---

## Phase 8: Deployment & Packaging

### Task 8.1: Local Run Script & Documentation
* **Purpose:** Single-command startup scripts (`start.sh` / `start.bat`) to launch backend and frontend simultaneously.
* **Files Affected:** `README.md`, `start.sh`
* **Dependencies:** Phase 6
* **Priority:** P1
* **Completion Criteria:** Clean developer setup within 2 minutes.
