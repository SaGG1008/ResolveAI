# ResolveAI --- System Architecture

**Version:** 1.0\
**Project:** AI IT Service Desk Autonomous Resolution Agent

## 1. Architecture Objective

ResolveAI implements an agentic workflow that transforms a
natural-language employee IT issue into:

**Evidence → Diagnosis → Action → Verification → Resolution/Escalation**

The architecture is intentionally modular so that the LLM, retrieval
layer, tools, and UI can evolve independently.

------------------------------------------------------------------------

## 2. High-Level Architecture

``` text
┌───────────────────────────────────────────────┐
│                  USER / IT STAFF              │
└──────────────────────┬────────────────────────┘
                       │
                       ▼
┌───────────────────────────────────────────────┐
│             React + TypeScript UI             │
│ Dashboard / Incident / Agent Trace / Evidence │
└──────────────────────┬────────────────────────┘
                       │ HTTP / Streaming
                       ▼
┌───────────────────────────────────────────────┐
│                  FastAPI                      │
│ Incident API / Approval / Execution / Status │
└──────────────────────┬────────────────────────┘
                       │
                       ▼
┌───────────────────────────────────────────────┐
│              Agent Orchestrator               │
│                                               │
│ Triage → Investigation → Diagnosis            │
│          → Action Planner → Verification      │
└─────────────┬─────────────────┬───────────────┘
              │                 │
              ▼                 ▼
┌──────────────────────┐ ┌─────────────────────┐
│ Retrieval / Data     │ │ Controlled Tools    │
│                      │ │                     │
│ Knowledge Base       │ │ VPN Reset           │
│ Previous Tickets     │ │ Service Restart     │
│ System Status        │ │ DNS Clear           │
│ Procedures           │ │ Ticket Creation     │
└──────────────────────┘ │ Escalation          │
                         │ Verification        │
                         └─────────────────────┘
```

------------------------------------------------------------------------

## 3. Architectural Layers

### Layer 1 --- Presentation

Responsibilities: - issue submission, - incident monitoring, - agent
activity, - evidence display, - action approval, - resolution state.

Technology: - React, - TypeScript, - Tailwind CSS.

### Layer 2 --- API

Responsibilities: - receive incidents, - expose incident state, - handle
approval, - expose agent events, - trigger execution.

Technology: - Python, - FastAPI, - Pydantic.

### Layer 3 --- Orchestration

Responsibilities: - maintain incident state, - invoke agents, - enforce
state transitions, - route tool calls, - handle failures, - trigger
escalation.

### Layer 4 --- Agent Layer

Five logical agents:

``` text
Triage
Investigation
Diagnosis
Action Planner
Verification / Escalation
```

### Layer 5 --- Retrieval / Data

Provides: - knowledge, - historical tickets, - service status, -
approved procedures.

### Layer 6 --- Tool Layer

Provides controlled actions: - reset, - restart, - clear, - create
ticket, - escalate, - verify.

------------------------------------------------------------------------

## 4. Incident State Machine

``` text
RECEIVED
   ↓
TRIAGING
   ↓
INVESTIGATING
   ↓
DIAGNOSING
   ↓
PLANNING_ACTION
   ↓
AWAITING_APPROVAL
   ↓
EXECUTING
   ↓
VERIFYING
   ├───────────────┐
   ↓               ↓
RESOLVED        ESCALATED
```

`AWAITING_APPROVAL` can be skipped for low-risk pre-approved actions.

------------------------------------------------------------------------

## 5. Agent Communication

Agents should communicate using structured objects rather than
unrestricted natural-language handoffs.

Example:

``` json
{
  "incident_id": "INC-1042",
  "agent": "diagnosis",
  "input": {
    "evidence": []
  },
  "output": {
    "diagnosis": "Expired VPN token",
    "confidence": 0.91,
    "evidence_ids": ["KB-104", "INC-421"]
  }
}
```

This makes agent transitions testable and auditable.

------------------------------------------------------------------------

## 6. Tool Registry

``` text
Tool Registry
├── search_knowledge_base
├── search_previous_tickets
├── get_system_status
├── get_troubleshooting_procedure
├── reset_vpn_token
├── restart_service
├── clear_dns_cache
├── create_ticket
├── escalate_to_human
└── verify_resolution
```

The Action Planner can only select tools from this registry.

------------------------------------------------------------------------

## 7. Data Architecture

### MVP Storage

Use: - JSON for static reference data, - SQLite for incident state if
persistence is required.

### Data Sources

``` text
data/
├── knowledge_base.json
├── tickets.json
├── system_status.json
└── procedures.json
```

### Incident State

Incident records should contain:

``` text
identity
issue
classification
agent trace
evidence
diagnosis
action plan
execution
verification
final status
```

------------------------------------------------------------------------

## 8. Retrieval Architecture

``` text
Issue
 ↓
Triage Query
 ↓
Retriever
 ├── Knowledge Base
 ├── Previous Tickets
 ├── Procedures
 └── Status
 ↓
Evidence Set
 ↓
Diagnosis
```

Every retrieved item should preserve its source identifier.

The MVP can begin with lightweight semantic/keyword retrieval. A vector
database is optional and should not be allowed to delay the core demo.

------------------------------------------------------------------------

## 9. API Architecture

### `POST /api/incidents`

Creates and starts an incident.

### `GET /api/incidents/{id}`

Returns current incident state.

### `POST /api/incidents/{id}/execute`

Executes a selected approved action.

### `POST /api/incidents/{id}/approve`

Approves a human-review action.

### `POST /api/incidents/{id}/escalate`

Escalates the incident.

### Optional streaming endpoint

Used for agent activity updates.

------------------------------------------------------------------------

## 10. Real-Time Architecture

Preferred:

``` text
Agent Orchestrator
       ↓
Agent Event
       ↓
SSE / Streaming
       ↓
React Event Listener
       ↓
Agent Trace UI
```

Fallback for time constraints:

``` text
React
 ↓
Periodic GET /incident/{id}
 ↓
Updated agent state
```

------------------------------------------------------------------------

## 11. Security Architecture

Never implement:

``` text
LLM → Arbitrary Shell Command
```

Use:

``` text
LLM
 ↓
Tool Selection
 ↓
Allowlist
 ↓
Parameter Validation
 ↓
Risk / Approval Check
 ↓
Controlled Function
```

Secrets remain in environment variables.

------------------------------------------------------------------------

## 12. Failure Architecture

### LLM unavailable

→ Retry or escalate.

### Retrieval unavailable

→ Request more information or escalate.

### Tool fails

→ Record failure and do not claim success.

### Verification fails

→ Escalate.

### Evidence conflicts

→ Preserve conflict and reduce confidence; escalate if material.

------------------------------------------------------------------------

## 13. Deployment Model

For the hackathon:

``` text
Browser
   ↓
Frontend
   ↓
FastAPI
   ↓
Agent Orchestrator
   ↓
LLM + Local Data + Simulated Tools
```

Keep deployment simple. Production-grade infrastructure is outside the
MVP.

------------------------------------------------------------------------

## 14. Architectural Principle

> **Separate intelligence from authority.**

The LLM provides classification, investigation, diagnosis, and action
selection.

Application code provides: - permissions, - tool allowlists, -
validation, - execution, - verification, - escalation, - auditability.

This separation is the core technical safety boundary of ResolveAI.
