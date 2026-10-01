# GOALS — Project Objectives & Success Criteria

## ResolveAI — AI IT Service Desk Autonomous Resolution Agent

**Version:** 1.0  
**Target:** Hackathon MVP & Production Evolution  

---

## 1. Primary North Star Goal

Build a trustworthy, autonomous IT Service Desk agent that seamlessly transitions an employee issue from:
$$\text{Natural-Language Problem} \longrightarrow \text{Investigation} \longrightarrow \text{Evidence} \longrightarrow \text{Decision} \longrightarrow \text{Action} \longrightarrow \text{Verification} \longrightarrow \text{Resolution / Escalation}$$

The system must prove true **agentic intelligence**: multi-source reasoning, dynamic tool selection, evidence-grounded diagnosis, risk-bounded action execution, and active post-remediation verification.

---

## 2. User & Business Outcomes

* **Instant Employee Triage:** Reduce issue intake and initial diagnosis time from $15\text{–}30\text{ minutes}$ to $< 5\text{ seconds}$.
* **Autonomous Tier-1 Deflection:** Safely auto-resolve $40\text{–}60\%$ of repetitive tier-1 IT tickets without human intervention.
* **Eliminate Blind Script Execution:** Guarantee that every automated action is verified for real success before ticket closure.
* **Streamlined Human Escalation:** Equip Tier-2 IT support engineers with pre-assembled diagnostic briefs, eliminating repetitive discovery questions.

---

## 3. Technical & AI Goals

### 3.1 AI & Multi-Agent Goals
1. **Multi-Source Grounding:** Collect facts from KB articles, live system status checks, and past tickets.
2. **Zero Fabricated Evidence:** Diagnosis must explicitly cite retrieved evidence IDs; hallucinated troubleshooting is prevented by schema constraints.
3. **Dynamic Allowlisted Tool Selection:** The agent determines the appropriate remediation function based on diagnostic confidence.
4. **Active Verification:** Trigger post-action probes to confirm symptom relief before resolving the ticket.

### 3.2 Technical Engineering Goals
1. **Type-Safe Fullstack Contract:** Shared data models across React TypeScript and FastAPI Pydantic.
2. **Real-time Trace Streaming:** Stream agent thinking, actions, and status updates via Server-Sent Events (SSE).
3. **Deterministic Safety Guard:** Non-bypassable approval gates on elevated-risk tools.
4. **Sub-second Response Times:** High-performance local SQLite storage and optimized prompt pipelines.

---

## 4. Demo Scenarios & Acceptance Goals

The final demonstration will showcase 3 distinct, end-to-end incident scenarios:

### Scenario 1: Autonomous Low-Risk Resolution (VPN Connection Drop)
* **Prompt:** *"My VPN keeps dropping every 5 minutes and now says Authentication Session Expired."*
* **Investigation:** Discovers stale session lock in VPN Gateway telemetry + matching KB procedure.
* **Diagnosis:** Stale VPN session lock (Confidence: 0.94, Risk: `LOW`).
* **Action:** Automatically executes `reset_vpn_session(user_id)`.
* **Verification:** Probes gateway handshake $\rightarrow$ Verified Healthy.
* **Outcome:** Status transitions to `RESOLVED` with evidence drawer populated.

### Scenario 2: High-Risk Action with Human Approval (Internal Proxy Stall)
* **Prompt:** *"I can't reach the internal engineering git mirrors; connection refused on port 8080."*
* **Investigation:** Identifies crashed local auth proxy daemon.
* **Diagnosis:** Service crash (Confidence: 0.88, Risk: `MEDIUM`).
* **Action:** Selects `restart_service("auth_proxy")` $\rightarrow$ Triggers `AWAITING_APPROVAL`.
* **Human Action:** Operator reviews risk payload and clicks "Approve".
* **Execution & Verification:** Service restarts, probe verifies port 8080 active $\rightarrow$ Status transitions to `RESOLVED`.

### Scenario 3: Ambiguous Issue Escalation (Hardware / Kernel Failure)
* **Prompt:** *"My laptop screen started flickering purple then threw kernel code 0x889FA."*
* **Investigation:** KB search returns no conclusive match; telemetry shows unexpected hardware fault.
* **Diagnosis:** Low confidence diagnosis (Confidence: 0.32, Risk: `HIGH`).
* **Action:** Escalation agent generates Tier-2 Hardware Support ticket with full diagnostic brief.
* **Outcome:** Status transitions to `ESCALATED` with handover notes rendered in UI.

---

## 5. MVP Success Criteria

1. **End-to-End Execution:** All 3 scenarios complete with smooth UI animations and zero console errors.
2. **Explainability:** Users can inspect the exact evidence and thought logs behind every agent decision.
3. **Safety Verification:** The approval modal reliably halts medium/high-risk tool executions until explicitly authorized.
4. **Verification Enforcement:** An action is never assumed to be successful without a passing verification check.

---

## 6. Future & Production Readiness Goals

* Integration with live enterprise identity providers (Okta, Azure AD).
* Bi-directional connectors for ServiceNow, Jira Service Desk, and Zendesk.
* Vector database integration (BigQuery Vector Search, Pinecone, or pgvector) for enterprise-scale retrieval.
* Fine-tuned domain models for specialized enterprise IT diagnostics.
