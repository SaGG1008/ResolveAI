# ARCHITECTURE — System Architecture & Data Flow

## ResolveAI — AI IT Service Desk Autonomous Resolution Agent

**Version:** 1.0  
**Scope:** System Architecture, Component Modules, Data Flow, and Agent Pipeline  

---

## 1. High-Level Architecture Overview

ResolveAI is designed as an agentic operational platform that converts unstructured user problem reports into verified IT remediations through a clear separation of concerns across 6 distinct architectural tiers.

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        TIER 1: PRESENTATION (UI)                        │
│    React 19 + TypeScript + Vite                                         │
│    - Dashboard (KPIs, Incident Queue, System Health Overview)           │
│    - Incident Workspace (Live Activity Timeline, Evidence Drawer)       │
│    - Human Approval Modal (Risk Badge, Parameter Diff, Actions)         │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ REST / Server-Sent Events (SSE)
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          TIER 2: API & GATEWAY                          │
│    FastAPI Application Server                                           │
│    - Incident Management API (/api/incidents)                           │
│    - Real-Time Event Stream (/api/incidents/{id}/stream)                │
│    - Approval & Policy Enforcement Gate (/api/incidents/{id}/approval)  │
│    - Tool Directory & Telemetry (/api/tools, /api/health)               │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    TIER 3: ORCHESTRATION & STATE ENGINE                 │
│    Deterministic State Machine & Lifecycle Controller                   │
│    - State Transition Invariant Verifier                                │
│    - Event Dispatcher & SSE Broadcaster                                 │
│    - Risk & Approval Boundary Checks                                    │
└──────────────────────┬───────────────────────────────────┬──────────────┘
                       │                                   │
                       ▼                                   ▼
┌──────────────────────────────────────────────┐ ┌────────────────────────┐
│         TIER 4: MULTI-AGENT RUNTIME          │ │    TIER 5: STORAGE     │
│  1. Triage Agent (Category & Priority)       │ │ SQLite / SQLModel      │
│  2. Investigation Agent (RAG & Correlation)  │ │ - Incidents Table      │
│  3. Diagnosis Agent (Root Cause & Risk)      │ │ - Evidence Items Table │
│  4. Action Planner Agent (Tool Selection)    │ │ - Agent Traces Table   │
│  5. Verification Agent (Probe & Assertion)   │ │ - Tool Runs Audit Table│
│  6. Escalation Agent (Handover Package)      │ │ - Knowledge JSON Base  │
└──────────────────────┬───────────────────────┘ └────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   TIER 6: CONTROLLED TOOL REGISTRY                      │
│    Safe Sandboxed Execution Layer                                       │
│    - VPN Session Reset (`reset_vpn_session`)                            │
│    - Local DNS Cache Flush (`flush_dns_cache`)                          │
│    - Service Restart (`restart_service`) [Medium Risk / Approval Req]   │
│    - Jira Escalation Generator (`create_escalation_ticket`)             │
│    - Verification Prober (`run_connectivity_probe`)                     │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Directory & Module Responsibilities

### 2.1 Frontend Modules (`frontend/src/`)
* **`components/layout/`**: Structural layout frames, sidebar navigation, top header with status badges.
* **`components/dashboard/`**: High-level telemetry cards (Total Incidents, Auto-Resolved, Escalated, MTTR), recent incidents list.
* **`components/incident/`**: Main incident view, live status ribbon, problem details.
* **`components/agent/`**: The Agent Activity Trace component rendering step-by-step thoughts, actions taken, and execution status.
* **`components/evidence/`**: Interactive evidence cards and side-drawer displaying snippets from knowledge docs, status checks, and past tickets.
* **`components/common/`**: Reusable atomic UI elements (Buttons, Modals, Badges, Loaders).
* **`services/`**: Communication layer handling HTTP REST calls and SSE subscription streams with fallback mock data.
* **`context/`**: React Context providers managing active incident state, approvals, and global themes.

### 2.2 Backend Modules (`backend/app/`)
* **`api/`**: FastAPI routers defining REST and SSE endpoints for frontend consumption.
* **`core/state_machine.py`**: Enforces legal state transitions (`RECEIVED` $\rightarrow$ `TRIAGING` $\rightarrow$ `INVESTIGATING` $\rightarrow$ `DIAGNOSING` $\rightarrow$ `PLANNING_ACTION` $\rightarrow$ `EXECUTING` / `AWAITING_APPROVAL` $\rightarrow$ `VERIFYING` $\rightarrow$ `RESOLVED` / `ESCALATED`).
* **`agents/`**: Isolated prompt pipelines for each stage of incident resolution.
* **`tools/`**: Registry defining tool signatures, JSON schemas, risk classifications, and safe Python execution functions.
* **`models/`**: Pydantic schemas and database models ensuring end-to-end type safety.
* **`data/`**: Structured JSON seed files for knowledge base articles, past ticket embeddings/metadata, and simulated service statuses.

---

## 3. End-to-End Data & Request Flow

```
[Employee Client]
      │
      │ 1. POST /api/incidents { description, user_id }
      ▼
[FastAPI Router]
      │
      │ 2. Create DB Record (Status: RECEIVED)
      │ 3. Dispatch Async Orchestrator Task
      ▼
[Agent Orchestrator]
      │
      ├──▶ Step A: TriageAgent
      │      - Classifies issue -> Emits Trace Event -> State: TRIAGING
      │
      ├──▶ Step B: InvestigationAgent
      │      - Queries KB, System Status, Ticket Bank
      │      - Persists Evidence Items -> Emits Trace Event -> State: INVESTIGATING
      │
      ├──▶ Step C: DiagnosisAgent
      │      - Synthesizes root cause citing Evidence IDs
      │      - Computes Risk Level & Confidence -> State: DIAGNOSING
      │
      ├──▶ Step D: ActionPlannerAgent
      │      - Chooses Tool from Registry -> State: PLANNING_ACTION
      │      │
      │      ├── If Risk == LOW:
      │      │     State: EXECUTING -> Executes Handler
      │      │
      │      └── If Risk == MEDIUM or HIGH:
      │            State: AWAITING_APPROVAL -> Halts and broadcasts Approval Needed Event
      │            (User clicks Approve -> State: EXECUTING -> Executes Handler)
      │
      ├──▶ Step E: VerificationAgent
      │      - State: VERIFYING -> Runs probe against target system
      │      │
      │      ├── Probe Returns Healthy -> State: RESOLVED
      │      │
      │      └── Probe Returns Failed / Inconclusive -> State: ESCALATED
      │
      ▼
[Database & SSE Stream]
      │
      │ 4. Broadcast Real-time Events to Frontend
      ▼
[React UI Timeline & Evidence Cards Update]
```

---

## 4. AI Multi-Agent Workflow Specification

| Agent Role | Input Context | Output Schema | Safety Rule |
| :--- | :--- | :--- | :--- |
| **Triage Agent** | Raw natural language issue text, User profile | `category`, `urgency`, `impact`, `priority`, `intent` | No tool execution permitted. |
| **Investigation Agent** | Triage category, issue keywords | `evidence_items`: `[{ source, title, snippet, relevance }]` | Must cite source metadata; cannot hallucinate facts. |
| **Diagnosis Agent** | User issue + gathered `evidence_items` | `root_cause`, `confidence` ($0-1$), `cited_evidence_ids`, `risk_level` | Must link at least 1 evidence ID to its diagnosis. |
| **Action Planner** | Diagnosis, allowlisted tool signatures | `selected_tool`, `parameters`, `rationale`, `requires_approval` | Must select ONLY from the allowlist registry. |
| **Verification Agent** | Executed action result, user symptom context | `is_verified` (bool), `probe_type`, `probe_result`, `explanation` | Never accepts execution success alone as resolution. |
| **Escalation Agent** | Failed / Ambiguous context | `escalation_tier`, `reason`, `diagnostic_summary`, `handover_notes` | Generates structured handover summary. |

---

## 5. Security & Isolation Boundaries

1. **Deterministic Application Control:** The LLM does not execute code or shell scripts directly. It only emits structured parameters matching registered Python tool functions.
2. **Approval Enforcement:** The backend rejects direct execution calls for any action flagged `requires_approval = True` unless a signed approval session exists.
3. **Database Integrity:** Foreign key constraints between `incidents`, `evidence_items`, and `agent_traces` guarantee traceability.

---

## 6. Deployment Architecture

* **Local Development:**
  * Frontend served via Vite Dev Server on `http://localhost:5173`.
  * Backend served via Uvicorn on `http://localhost:8000`.
  * SQLite file storage in local repository directory.
* **Demo / Production Containerization:**
  * Multi-stage Dockerfile packaging FastAPI backend and compiled static React frontend into a unified lightweight container.
