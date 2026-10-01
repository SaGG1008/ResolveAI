# TRD — Technical Requirements Document

## ResolveAI — AI IT Service Desk Autonomous Resolution Agent

**Version:** 1.0  
**Status:** MVP Engineering Blueprint  
**System Type:** Multi-Agent Orchestration & Real-time Web Application  

---

## 1. Technical Overview

ResolveAI is constructed as a decoupled, multi-tier system comprising a reactive frontend interface, an asynchronous API server, and a deterministic multi-agent runtime. The architecture isolates non-deterministic LLM reasoning from deterministic tool execution, database mutations, and safety policy enforcement.

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (React 19 + TS)                 │
│         Dashboard, Incident Workspace, Trace, Evidence      │
└──────────────────────────────┬──────────────────────────────┘
                               │ REST / SSE Stream
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                  Backend (Python FastAPI)                   │
│         REST Endpoints, State Controller, Tool Registry     │
└──────────────────────────────┬──────────────────────────────┘
                               │
                ┌──────────────┴──────────────┐
                ▼                             ▼
┌─────────────────────────────┐ ┌─────────────────────────────┐
│    Multi-Agent Framework    │ │     Persistence Layer       │
│ Triage, Investigate,        │ │ SQLite / SQLModel Database  │
│ Diagnose, Act, Verify       │ │ In-memory Seed Datasets     │
└──────────────┬──────────────┘ └─────────────────────────────┘
               │
               ▼
┌─────────────────────────────┐
│      Controlled Tools       │
│ VPN Reset, DNS Flush, etc.  │
└─────────────────────────────┘
```

---

## 2. Technology Stack

### 2.1 Frontend
* **Core:** React 19, TypeScript 6.0+, Vite 8.3
* **Styling:** Vanilla CSS / Tailwind CSS compatibility layer (Custom theme variables and modular styling)
* **Icons:** SVG Icon system / Lucide icons
* **State & Networking:** React Context / Custom Hooks with Fetch & EventSource (Server-Sent Events)

### 2.2 Backend
* **Language & Framework:** Python 3.10+, FastAPI, Uvicorn
* **Data Validation & Schemas:** Pydantic v2
* **Storage & ORM:** SQLite with SQLModel / SQLAlchemy 2.0
* **Event Streaming:** Server-Sent Events (SSE) via `sse-starlette` or FastAPI `StreamingResponse`

### 2.3 AI & Agent Framework
* **LLM Engine:** Anthropic Claude API (claude-3-5-sonnet) / OpenAI API fallback
* **Agent Architecture:** Specialized functional agent classes (TriageAgent, InvestigationAgent, DiagnosisAgent, ActionPlannerAgent, VerificationAgent)
* **Prompt Engineering:** Pydantic Structured Outputs (JSON schema enforcement)

---

## 3. Frontend Architecture

### 3.1 Directory Structure (`frontend/src/`)
```
frontend/src/
├── assets/             # Static logos and illustrations
├── components/         # Reusable UI components
│   ├── layout/         # Sidebar, Header, PageContainer
│   ├── dashboard/      # KPICards, IncidentTable, SystemStatusWidget
│   ├── incident/       # IncidentHeader, IncidentSummary, StatusBadge
│   ├── agent/          # AgentTimeline, TraceStepItem, ThinkingSpinner
│   ├── evidence/       # EvidenceCard, EvidenceDrawer, SourceBadge
│   └── common/         # Button, Modal, Badge, RiskIndicator
├── context/            # IncidentContext, AuthContext, ThemeContext
├── hooks/              # useIncidentStream, useIncidents, useSystemStatus
├── services/           # api.ts, mockData.ts (fallback simulation)
├── types/              # incident.ts, agent.ts, evidence.ts, tool.ts
├── App.tsx             # Root router & view switcher
├── main.tsx            # React application entry point
├── App.css             # Component-level styles
└── index.css           # Global design tokens and root theme variables
```

### 3.2 State Management
* **Global Incident State:** React Context (`IncidentProvider`) holding active incident collection and current active incident.
* **Stream Synchronization:** Real-time updates delivered through SSE or optimistic polling updating the active agent timeline.

---

## 4. Backend Architecture

### 4.1 Directory Structure (`backend/`)
```
backend/
├── app/
│   ├── main.py              # FastAPI app initialization, CORS, routers
│   ├── config.py            # Environment configuration & Settings
│   ├── api/                 # Endpoint routers
│   │   ├── incidents.py     # Incident creation, lookup, listing
│   │   ├── approvals.py     # Action approval / rejection
│   │   ├── agent_events.py  # SSE event stream for live trace
│   │   └── tools.py         # Direct tool status & simulation
│   ├── core/                # Core engines
│   │   ├── state_machine.py # Incident state transitions & invariants
│   │   └── security.py      # Auth & parameter validation
│   ├── agents/              # Multi-agent implementations
│   │   ├── base.py          # BaseAgent class & prompt orchestrator
│   │   ├── triage.py        # Triage & categorization agent
│   │   ├── investigation.py # Multi-source retrieval & RAG agent
│   │   ├── diagnosis.py     # Root cause & risk scoring agent
│   │   ├── action_planner.py# Allowlisted tool selection agent
│   │   └── verification.py  # Health probe & verification agent
│   ├── tools/               # Controlled tool registry
│   │   ├── registry.py      # Allowlist & risk level metadata
│   │   └── handlers.py      # Concrete tool execution routines
│   ├── models/              # Pydantic schemas & DB models
│   │   ├── incident.py      # Incident model & state enum
│   │   ├── agent_trace.py   # Step logs, thoughts, decisions
│   │   ├── evidence.py      # Evidence items & sources
│   │   └── tool.py          # Execution requests & results
│   └── data/                # Knowledge base & seed data
│       ├── kb_articles.json # Troubleshooting guides
│       ├── past_tickets.json# Historical incident bank
│       └── system_status.json# Service availability mocks
├── requirements.txt         # Python dependencies
└── tests/                   # Pytest suite
```

---

## 5. Database Architecture

### 5.1 Technology
* **Engine:** SQLite (`resolveai.db`)
* **ORM:** SQLModel / SQLAlchemy (sync/async support)

### 5.2 Core Entities & Relations
* **`incidents`**: Primary ticket entity (`id`, `title`, `description`, `category`, `priority`, `status`, `created_at`, `updated_at`, `resolution_summary`).
* **`evidence_items`**: Evidence linked to incident (`id`, `incident_id`, `source_type`, `title`, `snippet`, `relevance_score`, `metadata_json`).
* **`agent_traces`**: Granular execution events (`id`, `incident_id`, `agent_name`, `step_type`, `thought`, `action`, `status`, `timestamp`).
* **`tool_executions`**: Audit trail of tool runs (`id`, `incident_id`, `tool_name`, `parameters_json`, `risk_level`, `requires_approval`, `approved_by`, `status`, `result_json`, `timestamp`).

---

## 6. AI & LLM Integration

### 6.1 LLM Client
* Invoked via official SDK with typed Pydantic output parsing.
* Temperature set to $0.0 - 0.2$ for deterministic reasoning and schema adherence.

### 6.2 Agent Prompting Invariants
* **Strict JSON Response Format:** All agents return strictly validated JSON structures.
* **Evidence Citations:** Diagnosis agents must reference active `evidence_id` values gathered by the Investigation agent.
* **Tool Allowlist Constraint:** Action planners can only output tool names present in the active tool registry schema.

---

## 7. State Machine & Incident Lifecycle

```
[RECEIVED] 
    │ (Triage Agent)
    ▼
[TRIAGING]
    │ (Investigation Agent)
    ▼
[INVESTIGATING]
    │ (Diagnosis Agent)
    ▼
[DIAGNOSING]
    │ (Action Planner Agent)
    ▼
[PLANNING_ACTION]
    │
    ├───────────────────────────────┐
    ▼ (Low Risk)                    ▼ (Medium/High Risk)
[EXECUTING]                   [AWAITING_APPROVAL]
    │                               │ (User Approves)
    │ ◄─────────────────────────────┘
    ▼
[VERIFYING] (Verification Agent)
    │
    ├───────────────────────────────┐
    ▼ (Verified Success)            ▼ (Failed Check / Ambiguous)
[RESOLVED]                    [ESCALATED]
```

---

## 8. Security & Error Handling

1. **Sandboxed Execution:** The LLM never directly runs shell commands or dynamic scripts. Tool names map to hardcoded Python functions in `tools/handlers.py`.
2. **Input Sanitization:** All incident inputs undergo validation against injection and length limits.
3. **Approval Gate Enforcement:** The API rejects any direct execution request for `MEDIUM`/`HIGH` risk tools unless an approval token/state is recorded.
4. **Resilient Fallbacks:** If LLM API fails or rate-limits, the system falls back to rule-based escalation and records a trace error without crashing the server.

---

## 9. Environment Variables

```env
# Application Settings
ENVIRONMENT=development
BACKEND_PORT=8000
FRONTEND_PORT=5173
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# AI & LLM Keys
ANTHROPIC_API_KEY=your-anthropic-api-key-here
OPENAI_API_KEY=your-openai-api-key-here

# Database
DATABASE_URL=sqlite:///./resolveai.db
```

---

## 10. Testing Strategy

* **Unit Testing:** Pytest covering tool registry, state machine transitions, and Pydantic parsing.
* **API Testing:** FastAPI `TestClient` verifying endpoint responses and status transitions.
* **Agent Integration Testing:** Mocked LLM responses ensuring predictable traversal through Scenarios 1, 2, and 3.
* **Frontend Verification:** Vite build check (`tsc -b && vite build`) and Oxlint linting.
