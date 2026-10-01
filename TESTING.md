# TESTING — Verification Strategy & Test Protocols

## ResolveAI — AI IT Service Desk Autonomous Resolution Agent

**Version:** 1.0  
**Frameworks:** Pytest (Backend), Vitest / React Testing Library (Frontend), Oxlint (Linting)  

---

## 1. Testing Strategy Overview

ResolveAI tests are partitioned into multi-layered verification gates ensuring deterministic safety, valid state transitions, reliable tool executions, and graceful failure handling.

```
┌────────────────────────────────────────────────────────┐
│             Level 5: Acceptance (Demo Scenarios)        │
├────────────────────────────────────────────────────────┤
│             Level 4: End-to-End API Integration        │
├────────────────────────────────────────────────────────┤
│             Level 3: Multi-Agent Pipeline & Fallback   │
├────────────────────────────────────────────────────────┤
│             Level 2: State Machine & Tool Registry     │
├────────────────────────────────────────────────────────┤
│             Level 1: Unit & Schema Validation          │
└────────────────────────────────────────────────────────┘
```

---

## 2. Test Suites & Protocols

### 2.1 Unit Testing (Level 1 & 2)
* **Pydantic Model Validation:** Verify that malformed payloads are rejected with descriptive errors.
* **Tool Registry Verification:**
  * Test that each registered tool (`reset_vpn_session`, `flush_dns_cache`, `restart_service`) executes its handler with valid parameters.
  * Test that tools reject invalid parameter types.
* **State Machine Invariants:**
  * Assert that illegal state transitions (e.g. `RECEIVED` $\rightarrow$ `RESOLVED` directly) raise `InvalidStateTransitionError`.
  * Assert that transitioning to `RESOLVED` without a prior `VERIFYING` state is rejected.

### 2.2 API Testing (Level 4)
* Using FastAPI `TestClient`:
  * `POST /api/incidents`: Validates incident creation and 201 response.
  * `GET /api/incidents/{id}`: Returns complete incident hierarchy (evidence, traces, diagnosis).
  * `POST /api/incidents/{id}/approval`:
    * Returns 200 and transitions state when incident is `AWAITING_APPROVAL`.
    * Returns 400 when incident is in any other state.

### 2.3 AI & Agent Pipeline Testing (Level 3)
* **Structured Output Enforcement:** Verify that LLM responses parse cleanly into target Pydantic schemas.
* **Evidence Citation Assertion:** Verify that `DiagnosisAgent` outputs include non-empty `cited_evidence_ids` corresponding to actual retrieved items.
* **Mock LLM Fallback:** Verify that with `ENABLE_MOCK_LLM=true`, the full pipeline executes deterministically without external network calls.

### 2.4 UI Testing
* **Component Rendering:** Ensure Dashboard, Incident Workspace, Evidence Drawer, and Approval Modal render without runtime exceptions.
* **Build Check:** Run `tsc -b && vite build` in `frontend/` to ensure zero compilation or type errors.
* **Linting:** Run `npm run lint` via Oxlint.

---

## 3. Demo Scenario Acceptance Criteria

| Scenario | Input Prompt | Expected Tool | Expected Approval Gate | Final State |
| :--- | :--- | :--- | :--- | :--- |
| **1. VPN Auto-Resolution** | "VPN dropping every 5 min..." | `reset_vpn_session` | No (Low Risk) | `RESOLVED` |
| **2. Auth Proxy Restart** | "Internal git mirrors connection refused..." | `restart_service` | **Yes (Medium Risk)** | `RESOLVED` (Post-Approval) |
| **3. Hardware / Kernel Fault** | "Flickering purple screen kernel 0x889FA" | `create_escalation_ticket` | No (Auto-Escalate) | `ESCALATED` |

---

## 4. Edge Case & Failure Mode Protocols

1. **Tool Execution Error:**
   * If a remediation tool raises an unexpected exception $\rightarrow$ Incident state machine captures error log, aborts resolution, and transitions to `ESCALATED`.
2. **Verification Failure:**
   * If post-remediation probe returns `is_verified: false` $\rightarrow$ System prevents `RESOLVED` and transitions to `ESCALATED`.
3. **Approval Rejection:**
   * If human operator clicks "Reject" in the approval modal $\rightarrow$ State transitions to `ESCALATED` with rejection notes recorded.
4. **Low LLM Confidence:**
   * If diagnosis confidence $< 0.70$ $\rightarrow$ System skips remediation and initiates human escalation.

---

## 5. Running the Tests

### 5.1 Backend Pytest Suite
```bash
cd backend
pytest tests/ -v
```

### 5.2 Frontend Build & Type Validation
```bash
cd frontend
npm run lint
npm run build
```
