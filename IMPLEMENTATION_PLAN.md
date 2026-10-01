# ResolveAI Implementation Plan

**Status:** Ready for Production Build
**Start Date:** 2026-10-01
**Target Delivery:** Hackathon MVP (3.5 hours)

---

## 1. Current State

The project consists of comprehensive documentation only:

- **ResolveAI_PRD.md** - Product requirements and vision
- **ResolveAI_TRD.md** - Technical architecture and implementation guidance
- **ResolveAI_AGENT_RULES.md** - Agent behavior constraints and principles
- **ResolveAI_GOALS.md** - Success metrics and demo scenarios
- **ResolveAI_UI_UX.md** - Design specifications and component layouts
- **ResolveAI_ARCHITECTURE.md** - System architecture and data flow

**No source code exists yet.** The project is ready for greenfield development.

---

## 2. Missing Components

### Entire Codebase Must Be Built:

- Frontend React application
- Backend FastAPI server
- Agent orchestration system
- Tool registry and controlled tools
- Retrieval layer (knowledge base, tickets, status, procedures)
- Data models and state management
- API endpoints
- Database/storage layer
- Testing framework

---

## 3. Technology Stack

**Frontend:**
- React 18+
- TypeScript
- Tailwind CSS
- Vite (build tool)

**Backend:**
- Python 3.10+
- FastAPI
- Pydantic
- SQLite or JSON storage

**Agent Layer:**
- Claude API (for LLM)
- Structured agent interfaces

**Data:**
- JSON files for controlled datasets
- SQLite for incident persistence

---

## 4. UI Implementation Plan (PHASE 1)

Building the interface first ensures the agentic workflow is visually obvious before backend integration.

### Priority Order:

1. **Project Setup & Component Architecture**
   - Initialize React + TypeScript + Tailwind
   - Create folder structure
   - Set up Vite build
   - Create mock data layer
   - Define TypeScript types for incidents, agents, evidence, etc.

2. **Layout & Navigation**
   - Sidebar navigation component
   - Main layout container
   - Header component
   - Responsive responsive grid system

3. **Dashboard Screen**
   - KPI cards (Active Incidents, AI Resolutions, Escalations)
   - New Incident CTA button
   - Recent Incidents table
   - System status overview

4. **New Incident Flow**
   - Issue description input
   - Investigation button
   - Incident created confirmation

5. **Incident Workspace (Most Important)**
   - Incident header with status
   - Two-column layout (Agent Activity | Incident Overview)
   - Agent Activity Timeline component
   - Incident Overview panel

6. **Evidence Component**
   - Evidence cards for KB, Tickets, Status, Procedures
   - Card layouts and styling
   - Expandable evidence details

7. **Diagnosis Component**
   - Likely cause display
   - Confidence indicator
   - Supporting evidence list
   - Uncertainty display

8. **Action Component**
   - Recommended action card
   - Risk level indicator
   - Approval status
   - Execute button
   - Explanation of evidence linking

9. **Approval Modal**
   - Human approval dialog
   - Risk display
   - Approve/Reject/Escalate buttons
   - Evidence summary

10. **Resolution/Escalation States**
    - Resolution card with full details
    - Escalation card with reason
    - Status indicators and timestamps

11. **Polish & Refinement**
    - Spacing and typography review
    - Responsive behavior testing
    - Dark mode verification
    - Animation and transitions
    - Loading states
    - Error states

---

## 5. Backend Implementation Plan (PHASE 2)

Build after UI foundation is complete.

### Components:

1. **FastAPI Setup**
   - Main app initialization
   - CORS configuration
   - Health check endpoint

2. **API Endpoints**
   - `POST /api/incidents` - Create incident
   - `GET /api/incidents/{id}` - Get incident state
   - `POST /api/incidents/{id}/execute` - Execute action
   - `POST /api/incidents/{id}/approve` - Approve action
   - `POST /api/incidents/{id}/escalate` - Escalate incident

3. **Data Models**
   - Incident state model
   - Agent event model
   - Evidence model
   - Diagnosis model
   - Action model

4. **Storage Layer**
   - Incident persistence
   - Event logging
   - Query interface

---

## 6. Agent Orchestration (PHASE 3)

Real agentic workflow implementation.

### Components:

1. **Orchestrator**
   - State machine for incident lifecycle
   - Agent sequencing
   - Error handling and escalation

2. **Triage Agent**
   - Issue classification
   - Priority assignment
   - Investigation queries

3. **Investigation Agent**
   - Knowledge base search
   - Ticket search
   - System status lookup
   - Procedure retrieval
   - Evidence aggregation

4. **Diagnosis Agent**
   - Evidence correlation
   - Root cause identification
   - Confidence calculation

5. **Action Planner**
   - Available action evaluation
   - Risk assessment
   - Approval requirement check
   - Action selection with evidence linking

6. **Verification Agent**
   - Post-action verification
   - Resolution determination
   - Escalation decision

---

## 7. Tool Layer (PHASE 4)

Controlled, allowlisted tools.

### Tools:

- `search_knowledge_base(query)` - Search KB articles
- `search_previous_tickets(query)` - Search incident history
- `get_system_status(service)` - Check service health
- `get_troubleshooting_procedure(issue_type)` - Get procedures
- `reset_vpn_token()` - Simulated VPN reset
- `restart_service(service)` - Simulated service restart
- `clear_dns_cache()` - Simulated DNS clear
- `create_ticket(summary, evidence, priority)` - Create ticket
- `escalate_to_human(reason, evidence)` - Escalate
- `verify_resolution(issue_type)` - Verify fix

### Data Sources:

- `data/knowledge_base.json` - KB articles
- `data/tickets.json` - Previous incidents
- `data/system_status.json` - Service status
- `data/procedures.json` - Troubleshooting procedures

---

## 8. Testing Plan (PHASE 5)

### Unit Tests:
- Agent schema validation
- Tool execution validation
- State transition logic
- Risk/approval checks

### Integration Tests:
- End-to-end incident flow
- Agent state transitions
- Tool execution sequencing

### Scenario Tests:
1. **VPN Auto Resolution** - Issue → Investigation → Diagnosis → Action → Verification → Resolved
2. **Email Issue Auto Resolution** - Similar flow for email service
3. **Security Issue Escalation** - Issue → Investigation → Risk Identified → Escalated

---

## 9. Production Order

### PHASE 1 — UI (1 hour)
- Project setup
- Component architecture
- Dashboard
- New Incident flow
- Incident workspace
- All UI components with mock data

**Stop Condition:** UI is polished with realistic mock data flowing through all screens.

### PHASE 2 — Backend API (30 minutes)
- FastAPI setup
- Incident endpoints
- Data models
- Storage layer

### PHASE 3 — Agent Orchestration (50 minutes)
- Orchestrator state machine
- Five agents with structured I/O
- Agent sequencing and error handling

### PHASE 4 — Tools + Data (30 minutes)
- Tool registry
- Controlled datasets
- Retrieval layer

### PHASE 5 — Integration (20 minutes)
- Wire frontend to backend
- Agent event streaming
- Real incident flow

### PHASE 6 — Testing & Polish (20 minutes)
- Scenario testing
- Visual polish
- Bug fixes

### PHASE 7 — Demo Prep (10 minutes)
- Final verification
- Demo scenario documentation

---

## 10. Critical Implementation Rules

1. **Do NOT rewrite unless necessary** - Use existing patterns
2. **Reuse components** - Build modular, reusable pieces
3. **Do NOT introduce new frameworks** - Stick to React + FastAPI
4. **Mock data first** - Build UI with realistic mock data before backend
5. **Separate concerns** - Keep data, presentation, and business logic distinct
6. **API-ready from day one** - UI must easily connect to real API
7. **No fake backend logic in UI** - Keep UI components pure
8. **Make agent workflow visible** - The UI must communicate the 5-agent flow
9. **Evidence-first design** - Show evidence before action decisions
10. **Safe, bounded autonomy** - Approval gates and escalation clearly visible

---

## 11. Success Criteria

### UI Completion (Phase 1):
- ✓ Dashboard visually communicates "AI IT Operations"
- ✓ New Incident flow works end-to-end
- ✓ Incident workspace shows agent timeline
- ✓ Evidence cards display correctly
- ✓ Diagnosis component shows confidence
- ✓ Action component is visually distinct
- ✓ Approval modal works
- ✓ Resolution/escalation states are clear
- ✓ Responsive at 1280px+ widths
- ✓ No console errors
- ✓ Design matches UI-UX.md specifications

### End-to-End (All Phases):
- ✓ Three demo scenarios complete successfully
- ✓ 100% of automated resolutions are verified
- ✓ 0 arbitrary tool executions
- ✓ 0 fabricated tool-success states
- ✓ Agent state is visible throughout
- ✓ Evidence is visible before action
- ✓ Judge understands product in <1 minute

---

## 12. Architecture Principles

**Separate intelligence from authority:**
- LLM provides: classification, investigation, diagnosis, action selection
- Application code provides: permissions, tool allowlists, validation, execution, verification, escalation, auditability

**This is the core safety boundary.**

---

## 13. Agentic Workflow (What the UI Must Show)

```
Issue Received
       ↓
Triage Agent (Classification)
       ↓
Investigation Agent (Evidence Collection)
       ├── Knowledge Base Search
       ├── Ticket Search
       ├── System Status
       └── Procedure Lookup
       ↓
Diagnosis Agent (Root Cause)
       ↓
Action Planner (Tool Selection)
       ↓
Approval Gate (Risk Check)
       ↓
Execute Approved Action
       ↓
Verification Agent (Did it work?)
       ├─→ YES: Resolved
       └─→ NO: Escalated
```

**The UI must make this flow visually obvious.**

---

## Next Steps

1. Initialize React + TypeScript + Tailwind project
2. Create mock data layer with realistic incident scenarios
3. Define TypeScript types for all domain objects
4. Build component architecture
5. Implement Dashboard screen
6. Implement Incident Workspace (2-column layout)
7. Implement all supporting components
8. Test with mock data
9. Polish and verify responsiveness
10. Begin Phase 2 (Backend)

---

**End Plan**
