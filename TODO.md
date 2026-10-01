# TODO — Prioritized Engineering Implementation Checklist

## ResolveAI — AI IT Service Desk Autonomous Resolution Agent

**Priority Legend:**
* `[P0]` Required for core MVP demo and essential system functionality.
* `[P1]` Important for system reliability, type safety, and error handling.
* `[P2]` Quality-of-life enhancements and UX polish.
* `[P3]` Post-hackathon enterprise extensions.

---

## 1. P0 — Core Demo Path Implementation

### Backend & Storage
- [x] `[P0]` Frontend UI/UX complete by Claude (`Dashboard`, `IncidentWorkspace`, `AgentTimeline`, `Sidebar`)
- [x] `[P0]` Implement Backend Pydantic Schemas matching frontend types (`backend/app/models/schemas.py`)
- [x] `[P0]` Implement SQLite/JSON Persistence Engine (`backend/app/core/db.py`)
- [x] `[P0]` Implement Seed Datasets for KB, past tickets, and system status (`backend/app/data/`)
- [x] `[P0]` Implement Controlled Tool Registry & Allowlisted Handlers (`backend/app/tools/`)

### Multi-Agent Orchestrator & State Engine
- [x] `[P0]` Implement Triage Agent (`backend/app/agents/triage.py`)
- [x] `[P0]` Implement Investigation Agent with RAG & Evidence retrieval (`backend/app/agents/investigation.py`)
- [x] `[P0]` Implement Diagnosis Agent with evidence citation (`backend/app/agents/diagnosis.py`)
- [x] `[P0]` Implement Action Planner Agent with risk evaluation & approval gate (`backend/app/agents/action_planner.py`)
- [x] `[P0]` Implement Verification Agent with post-remediation probes (`backend/app/agents/verification.py`)
- [x] `[P0]` Implement Orchestrator coordinating full event stream & state transitions (`backend/app/agents/orchestrator.py`)

### API & Streaming Endpoints
- [x] `[P0]` Implement FastAPI Server with CORS & Error Handling (`backend/app/main.py`)
- [x] `[P0]` Implement Incident CRUD & Investigation Trigger APIs (`backend/app/api/incidents.py`)
- [x] `[P0]` Implement Action Approval API (`backend/app/api/incidents.py`)
- [x] `[P0]` Implement Server-Sent Events (SSE) stream (`backend/app/api/incidents.py`)
- [x] `[P0]` Implement Dashboard Metrics API (`backend/app/api/dashboard.py`)
- [x] `[P0]` Implement System Health & Status endpoint (`backend/app/api/system.py`)

### Frontend Integration
- [x] `[P0]` Implement API Client and SSE live stream listener in Frontend (`frontend/src/services/api.ts`)
- [x] `[P0]` Wire New Incident modal and quick demo scenarios into UI (`frontend/src/App.tsx`)
- [x] `[P0]` Wire Approval button to `/api/incidents/{id}/approval` (`frontend/src/components/IncidentWorkspace.tsx`)
- [x] `[P0]` Validate Scenario 1: VPN Auto-Resolution
- [x] `[P0]` Validate Scenario 2: Auth Proxy Restart Approval
- [x] `[P0]` Validate Scenario 3: Hardware Escalation

---

## 2. P1 — Important Enhancements
- [x] `[P1]` Structured logging and health check endpoints
- [x] `[P1]` Automated test suite for backend state transitions and agent pipeline (`backend/tests/test_backend.py`)
- [x] `[P1]` Unified startup scripts for backend and frontend (`start.bat`, `start.sh`)
- [x] `[P1]` Zero-warning Oxlint and zero-error TypeScript build
- [ ] `[P1]` Dark/light mode theme toggle button in Sidebar

---

## 3. P2 & P3 — Future Scope
- [ ] `[P2]` Additional automated tools (e.g. disk space cleanup, certificate refresh)
- [ ] `[P3]` Enterprise SSO/SAML identity provider connector
- [ ] `[P3]` Live Jira / ServiceNow bidirectional webhook synchronization
