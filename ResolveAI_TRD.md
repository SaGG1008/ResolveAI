# TRD --- ResolveAI

## AI IT Service Desk Autonomous Resolution Agent

**Version:** 1.0\
**Status:** Hackathon MVP / Demo-Ready Prototype\
**Source:** ResolveAI PRD v1.0

------------------------------------------------------------------------

# 1. Technical Objective

ResolveAI is a controlled Agentic AI system that transforms a
natural-language IT issue into an evidence-backed resolution or human
escalation.

The technical system must implement:

``` text
Issue Intake
    ↓
Triage
    ↓
Investigation
    ├── Knowledge Base / RAG
    ├── Previous Tickets
    ├── System Status
    └── Troubleshooting Procedures
    ↓
Diagnosis
    ↓
Action Planning
    ↓
Approval / Risk Check
    ↓
Tool Execution
    ↓
Verification
    ↓
Resolved / Escalated
```

The implementation priority is:

**Agent behavior \> integrations \> feature count**

------------------------------------------------------------------------

# 2. Recommended Architecture

``` text
┌──────────────────────────────────────────────┐
│                  Frontend                    │
│        React + TypeScript + Tailwind         │
└──────────────────────┬───────────────────────┘
                       │ HTTP / JSON
                       ▼
┌──────────────────────────────────────────────┐
│                 FastAPI API                  │
│      Incident API / Agent Run API / Data     │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│             Agent Orchestrator               │
│                                              │
│ Triage → Investigation → Diagnosis → Action  │
│                         Planner → Verify     │
└──────────────┬──────────────┬────────────────┘
               │              │
               ▼              ▼
┌─────────────────────┐  ┌────────────────────┐
│ Retrieval / Data    │  │ Controlled Tools   │
│                     │  │                    │
│ Knowledge Base      │  │ VPN Reset          │
│ Tickets             │  │ Service Restart    │
│ System Status       │  │ DNS Clear          │
│ Procedures          │  │ Ticket Creation    │
└─────────────────────┘  │ Escalation         │
                         │ Verification       │
                         └────────────────────┘
```

------------------------------------------------------------------------

# 3. Technology Stack

## Frontend

-   React
-   TypeScript
-   Tailwind CSS
-   Modern browser-based SPA architecture
-   Server-Sent Events or WebSocket-style streaming may be added for
    live agent status if time permits

## Backend

-   Python
-   FastAPI
-   Pydantic
-   Async request handling where useful

## Agent Layer

Use the LLM/API provider already available to the development
environment.

The architecture should isolate model calls behind an internal interface
so the provider can be replaced without changing agent business logic.

## Data

For the MVP:

-   JSON files for fastest setup, or
-   SQLite if persistent incident records are required.

No production database is required for the hackathon.

## Retrieval

Use a lightweight retrieval layer over the controlled knowledge base.

Preferred order:

1.  Simple semantic/keyword retrieval if time is limited.
2.  Embedding-based retrieval if already available.
3.  Full vector database only if it can be added without risking the
    demo.

------------------------------------------------------------------------

# 4. Repository Structure

``` text
resolve-ai/
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── hooks/
│   │   ├── services/
│   │   ├── types/
│   │   └── App.tsx
│   └── package.json
│
├── backend/
│   ├── app/
│   │   ├── main.py
│   │   ├── api/
│   │   ├── agents/
│   │   ├── tools/
│   │   ├── retrieval/
│   │   ├── models/
│   │   ├── services/
│   │   └── config.py
│   └── requirements.txt
│
├── data/
│   ├── knowledge_base.json
│   ├── tickets.json
│   ├── system_status.json
│   └── procedures.json
│
├── docs/
│   ├── PRD.md
│   ├── TRD.md
│   ├── AGENT-RULES.md
│   ├── UI-UX.md
│   ├── GOALS.md
│   └── ACHIEVEMENTS.md
│
├── tests/
│
├── .env.example
└── README.md
```

------------------------------------------------------------------------

# 5. Backend Architecture

## 5.1 API Layer

FastAPI should expose a small number of endpoints.

### Create / Run Incident

``` http
POST /api/incidents
```

Request:

``` json
{
  "description": "My VPN stopped working this morning.",
  "user_id": "demo-user-01"
}
```

Response:

``` json
{
  "incident_id": "INC-1042",
  "status": "investigating"
}
```

### Get Incident

``` http
GET /api/incidents/{incident_id}
```

Returns:

-   issue
-   category
-   priority
-   agent states
-   evidence
-   diagnosis
-   selected action
-   execution result
-   verification
-   final status

### Execute Approved Action

``` http
POST /api/incidents/{incident_id}/execute
```

Used when an action requires explicit UI execution or approval.

### Approve Action

``` http
POST /api/incidents/{incident_id}/approve
```

### Escalate

``` http
POST /api/incidents/{incident_id}/escalate
```

------------------------------------------------------------------------

# 6. Agent Orchestration

The orchestrator controls the lifecycle of an incident.

## State Machine

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
AWAITING_APPROVAL ─────┐
   ↓                   │
EXECUTING              │
   ↓                   │
VERIFYING              │
   ↓                   │
RESOLVED               │
                       │
FAILED / UNSAFE ───────┘
   ↓
ESCALATED
```

The orchestrator should maintain a structured incident state rather than
relying on conversation history alone.

------------------------------------------------------------------------

# 7. Agent Contracts

Each agent should have a predictable input/output schema.

## 7.1 Triage Agent

### Input

``` json
{
  "description": "string",
  "user_context": {}
}
```

### Output

``` json
{
  "category": "VPN",
  "intent": "connection_failure",
  "priority": "medium",
  "investigation_queries": [
    "VPN authentication failure"
  ]
}
```

------------------------------------------------------------------------

## 7.2 Investigation Agent

### Input

``` json
{
  "category": "VPN",
  "queries": []
}
```

### Output

``` json
{
  "knowledge_results": [],
  "previous_tickets": [],
  "system_status": {},
  "procedures": [],
  "evidence": []
}
```

Every evidence item should contain a source identifier.

------------------------------------------------------------------------

## 7.3 Diagnosis Agent

### Input

Investigation results.

### Output

``` json
{
  "diagnosis": "Expired VPN authentication token",
  "confidence": 0.91,
  "supporting_evidence": [
    "KB-104",
    "INC-421",
    "VPN-STATUS-01"
  ],
  "uncertainties": []
}
```

The model must not invent evidence IDs.

------------------------------------------------------------------------

## 7.4 Action Planner

### Input

Diagnosis + available procedures + evidence.

### Output

``` json
{
  "selected_action": "reset_vpn_token",
  "risk_level": "low",
  "approval_required": false,
  "reason": "Evidence indicates an authentication-token issue.",
  "rejected_actions": [
    {
      "action": "restart_vpn_service",
      "reason": "VPN infrastructure is operational."
    }
  ]
}
```

------------------------------------------------------------------------

## 7.5 Verification Agent

### Input

Action result + original incident.

### Output

``` json
{
  "verified": true,
  "verification": "VPN authentication successful",
  "final_status": "resolved"
}
```

If verification fails:

``` json
{
  "verified": false,
  "final_status": "escalated"
}
```

------------------------------------------------------------------------

# 8. Tool Architecture

Tools must be deterministic and controlled.

## Tool Interface

Each tool should expose:

``` text
name
description
input_schema
output_schema
risk_level
approval_required
execute()
```

## Tool Registry

Example:

``` python
TOOLS = {
    "search_knowledge_base": ...,
    "search_previous_tickets": ...,
    "get_system_status": ...,
    "get_troubleshooting_procedure": ...,
    "reset_vpn_token": ...,
    "restart_service": ...,
    "clear_dns_cache": ...,
    "create_ticket": ...,
    "escalate_to_human": ...,
    "verify_resolution": ...
}
```

The Action Planner may select only tools registered in this allowlist.

------------------------------------------------------------------------

# 9. Safety / Permission Layer

Before execution:

``` text
Agent-selected action
        ↓
Tool exists?
        ↓
Procedure permits it?
        ↓
Risk acceptable?
        ↓
Approval required?
   ↙            ↘
No              Yes
↓                ↓
Execute       Human Approval
```

Rules:

1.  Unknown tools cannot execute.
2.  Destructive or sensitive actions cannot execute automatically.
3.  A failed tool call cannot be reported as successful.
4.  The agent cannot fabricate tool results.
5.  Human escalation is always available.
6.  Verification is required before declaring resolution.

------------------------------------------------------------------------

# 10. Retrieval Architecture

## Knowledge Base

The MVP knowledge base contains structured troubleshooting documents.

Example:

``` json
{
  "id": "KB-104",
  "title": "VPN Authentication Troubleshooting",
  "category": "VPN",
  "symptoms": [
    "VPN stopped working",
    "authentication failure"
  ],
  "solution": "Reset the VPN authentication token.",
  "approved_actions": [
    "reset_vpn_token"
  ]
}
```

## Retrieval Flow

``` text
User Issue
   ↓
Triage Query
   ↓
Retriever
   ↓
Top Relevant Documents
   ↓
Evidence Set
   ↓
Diagnosis Agent
```

The retrieved source ID must remain attached to the evidence.

------------------------------------------------------------------------

# 11. Data Schemas

## Incident

``` json
{
  "incident_id": "INC-1042",
  "user_id": "demo-user-01",
  "description": "My VPN stopped working.",
  "category": "VPN",
  "priority": "medium",
  "status": "resolved",
  "agent_trace": [],
  "evidence": [],
  "diagnosis": {},
  "action_plan": {},
  "execution": {},
  "verification": {}
}
```

## Agent Event

``` json
{
  "timestamp": "ISO-8601",
  "agent": "investigation",
  "status": "completed",
  "summary": "Found 3 relevant evidence sources",
  "duration_ms": 820
}
```

The frontend uses these events to render the live Agent Activity Trace.

------------------------------------------------------------------------

# 12. Frontend Architecture

## Main Routes

``` text
/
├── Dashboard
├── Incidents
├── Incidents/:id
├── Knowledge Base
├── System Status
└── Analytics
```

For the 3.5-hour MVP, Dashboard and Incident Details are the highest
priority.

## Core Components

``` text
Dashboard
├── MetricCards
├── NewIssuePanel
├── RecentIncidents
└── AgentActivity

IncidentDetails
├── IncidentHeader
├── AgentTrace
├── EvidencePanel
├── DiagnosisCard
├── ActionPanel
├── ApprovalModal
├── ExecutionTimeline
└── ResolutionCard
```

------------------------------------------------------------------------

# 13. Real-Time Agent Updates

Preferred approach:

``` text
Backend Agent Event
       ↓
SSE / streaming endpoint
       ↓
Frontend event listener
       ↓
Agent Trace update
```

Example events:

``` json
{
  "type": "agent_started",
  "agent": "investigation"
}
```

``` json
{
  "type": "tool_completed",
  "tool": "search_knowledge_base",
  "result_count": 3
}
```

``` json
{
  "type": "agent_completed",
  "agent": "diagnosis"
}
```

If streaming becomes a time risk, polling the incident endpoint is an
acceptable MVP fallback.

------------------------------------------------------------------------

# 14. Error Handling

## LLM Failure

Show:

``` text
AI investigation temporarily unavailable.
Please retry or escalate to IT support.
```

## Tool Failure

The system must record:

``` text
Tool:
reset_vpn_token

Status:
FAILED

Reason:
Simulated service unavailable
```

It must NOT show "Resolved."

## Retrieval Failure

Fall back to:

-   request additional information,
-   create incident,
-   escalate.

## Verification Failure

Automatically transition to escalation unless another safe action is
available.

------------------------------------------------------------------------

# 15. Observability

Each incident should record:

-   agent execution sequence,
-   tool calls,
-   tool results,
-   timestamps,
-   selected action,
-   rejected actions,
-   approval state,
-   final outcome.

For the hackathon, logs can be stored locally.

Example:

``` text
INC-1042
├── triage.completed
├── kb_search.completed
├── ticket_search.completed
├── system_status.completed
├── diagnosis.completed
├── action_selected
├── vpn_reset.executed
├── verification.completed
└── incident.resolved
```

------------------------------------------------------------------------

# 16. Security Boundaries

The MVP must use simulated actions.

Do not expose arbitrary shell execution through the LLM.

Do not allow:

``` text
LLM → arbitrary command execution
```

Instead:

``` text
LLM
 ↓
Allowlisted Tool
 ↓
Validated Parameters
 ↓
Controlled Function
```

Environment secrets must be stored in `.env` and never committed.

------------------------------------------------------------------------

# 17. Testing Strategy

## Unit Tests

Test:

-   triage schema validation,
-   tool schema validation,
-   risk checks,
-   approval checks,
-   state transitions,
-   verification behavior.

## Integration Tests

Test:

``` text
Issue → Triage → Investigation → Diagnosis → Action → Verification
```

## Scenario Tests

### Test 1

VPN issue → automatic resolution.

### Test 2

Email issue → automatic resolution.

### Test 3

Security-sensitive issue → human escalation.

### Test 4

Tool failure → no false resolution.

### Test 5

Verification failure → escalation.

------------------------------------------------------------------------

# 18. Demo Reliability Strategy

The hackathon demo should use controlled scenarios.

Recommended design:

``` text
Demo Mode
   ↓
Known Dataset
   ↓
Deterministic Tool Results
   ↓
Real Agent Orchestration
```

The agents should still make the decisions dynamically, while the
underlying simulated enterprise environment remains predictable.

This minimizes demo failure without reducing the visible agentic
behavior.

------------------------------------------------------------------------

# 19. Performance Targets

For the MVP:

-   UI should respond immediately to issue submission.
-   Agent progress should be visible during execution.
-   Tool calls should generally complete within a few seconds.
-   The complete demo scenario should finish quickly enough for a live
    presentation.
-   No individual slow operation should leave the user without status
    information.

Exact latency targets are not specified by the PRD and should be treated
as practical hackathon targets rather than contractual requirements.

------------------------------------------------------------------------

# 20. Implementation Priorities

## P0 --- Mandatory

1.  Agent orchestrator
2.  Five logical agents
3.  Tool registry
4.  Knowledge retrieval
5.  Ticket retrieval
6.  System status
7.  Action execution
8.  Verification
9.  Escalation
10. Agent trace
11. Evidence UI
12. Three working scenarios

## P1 --- Important

-   Streaming agent status
-   Approval modal
-   Confidence indicator
-   Incident history
-   Action timeline

## P2 --- Optional

-   Analytics
-   Real ITSM integrations
-   Authentication
-   Advanced vector database
-   External monitoring
-   Enterprise deployment

------------------------------------------------------------------------

# 21. 3.5-Hour Engineering Schedule

## 00:00--00:20

Repository, schemas, interfaces.

## 00:20--01:10

Agent orchestration and LLM integration.

## 01:10--01:40

Tools and controlled datasets.

## 01:40--02:40

Frontend dashboard and incident view.

## 02:40--03:05

End-to-end integration.

## 03:05--03:25

Testing and visual polish.

## 03:25--03:30

Feature freeze and demo verification.

------------------------------------------------------------------------

# 22. Technical Definition of Done

The technical implementation is complete when:

-   [ ] Frontend can create an incident.
-   [ ] Backend creates a persistent incident state.
-   [ ] Triage returns structured output.
-   [ ] Investigation retrieves evidence from multiple sources.
-   [ ] Diagnosis references evidence.
-   [ ] Action Planner chooses from an allowlisted tool registry.
-   [ ] Risk/approval policy is enforced.
-   [ ] Tool execution returns structured results.
-   [ ] Verification determines success/failure.
-   [ ] Failed actions cannot produce false "resolved" states.
-   [ ] Escalation works.
-   [ ] Agent events appear in the UI.
-   [ ] Evidence appears in the UI.
-   [ ] Three end-to-end scenarios pass.
-   [ ] No arbitrary system commands can be triggered by the model.
-   [ ] Demo can run reliably from a clean start.

------------------------------------------------------------------------

# 23. Architecture Principle

The core technical principle is:

> **The LLM decides; controlled application code enforces what the agent
> is allowed to do.**

This keeps the system visibly agentic while maintaining deterministic
tool boundaries, safety controls, verification, and reliable hackathon
behavior.
