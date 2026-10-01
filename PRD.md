# PRD — ResolveAI

## AI IT Service Desk Autonomous Resolution Agent

**Version:** 1.0  
**Status:** Hackathon MVP / Demo-Ready Architecture  
**Primary Objective:** Build an Agentic AI IT Service Desk that investigates employee IT issues, gathers multi-source evidence, formulates reasoned diagnoses, selects allowlisted remediation actions, executes safe low-risk resolutions, verifies actual outcome state, and escalates unresolved or high-risk incidents to human operators.

---

## 1. Product Overview

### 1.1 Product Name
**ResolveAI**

### 1.2 Product Concept
ResolveAI is an agentic IT service desk platform engineered around the core paradigm:
$$\text{Natural-Language Problem} \longrightarrow \text{Investigation} \longrightarrow \text{Evidence} \longrightarrow \text{Decision} \longrightarrow \text{Action} \longrightarrow \text{Verification} \longrightarrow \text{Resolution / Escalation}$$

Rather than functioning as a standard conversational chatbot that regurgitates generic documentation, ResolveAI acts as an autonomous tier-1 technical support engineer. It correlates live telemetry, historical incident tickets, and knowledge bases to execute concrete, safe remediations with full auditability and post-execution verification.

---

## 2. Problem Statement

Modern enterprise IT support faces critical operational bottlenecks:
1. **High Volume of Repetitive Tickets:** 40–60% of tier-1 tickets (VPN disconnects, credential locks, DNS cache corruption, minor service stalls) are routine yet consume immense staff hours.
2. **Disconnected Context & Evidence:** Information needed for accurate diagnosis is siloed across knowledge bases, active telemetry/status boards, and past ticket logs.
3. **Chatbot Limitations:** First-generation IT chatbots provide static text links without the capability to query live system states, make safe policy-checked decisions, or execute remediation actions.
4. **Lack of Post-Execution Verification:** Automated scripts frequently assume success upon dispatch without verifying whether the underlying user symptom was truly mitigated.

ResolveAI bridges this gap through an evidence-backed, multi-agent orchestration pipeline with deterministic guardrails.

---

## 3. Target Users & Personas

### 3.1 Primary Persona: Enterprise Employee (End User)
* **Profile:** Non-technical or technical employee encountering workplace IT roadblocks (e.g., VPN drops, SaaS access denial, local disk exhaustion).
* **Needs:** Instant issue intake, transparent progress tracking, zero technical jargon required, rapid resolution without waiting hours in a human queue.

### 3.2 Secondary Persona: IT Service Desk Operations & Approvers (Tier 2/3 Staff)
* **Profile:** IT support engineers, sysadmins, and security leads managing escalations.
* **Needs:** Clear evidence trails, audit logs of agent reasoning, interactive approval gates for elevated-risk actions (e.g., service restarts, permissions adjustments), and seamless ticket escalation summaries.

---

## 4. Goals & Non-Goals

### 4.1 Core Goals
* **G1: Natural Language Intake:** Ingest and parse arbitrary employee issue descriptions into structured classifications (category, severity, intent).
* **G2: Multi-Source Investigation (RAG):** Automatically query internal KB articles, system status monitors, and historical tickets to synthesize relevant context.
* **G3: Grounded Evidence Formulation:** Require all diagnostic conclusions to cite explicit evidence items; prevent hallucinated troubleshooting steps.
* **G4: Dynamic Tool Selection:** Select an appropriate allowlisted remediation tool based on evidence and system state.
* **G5: Safety & Approval Gates:** Enforce approval requirements for any medium-to-high risk or mutating actions.
* **G6: Post-Remediation Verification:** Execute an active health/connectivity check following remediation to confirm real resolution before closing an incident.
* **G7: Graceful Escalation:** Escalate to Tier-2 human technicians with a pre-assembled diagnostic brief when automated resolution is infeasible, ambiguous, or failed.
* **G8: Transparent Agent Activity Trace:** Provide real-time UI visibility into agent steps, thought processes, tool inputs/outputs, and decision logs.

### 4.2 Non-Goals (MVP Scope Boundaries)
* Direct kernel-level or Active Directory modification on physical user workstations without sandboxed simulation.
* Real enterprise ServiceNow / Jira API production write-backs (mocked/simulated storage for MVP).
* Unrestricted shell or arbitrary command execution by the LLM.
* Autonomous execution of high-risk financial or global security policy modifications.

---

## 5. Core Features & Functional Requirements

### 5.1 Issue Intake & Triage
* Accepts freeform text and optional metadata (user ID, department, operating system).
* Generates structured triage outputs: `category`, `urgency`, `impact`, `priority` ($P1$ to $P4$), and `initial_hypothesis`.

### 5.2 Multi-Agent Investigation Engine
* **Knowledge Retrieval:** Searches indexed IT manuals and KB articles.
* **Telemetry & Status Lookup:** Queries simulated health states of enterprise services (VPN Gateway, SSO, Mail Server).
* **Historical Ticket Correlation:** Finds matching resolved tickets with similar symptom vectors.

### 5.3 Diagnostic & Decision Engine
* Synthesizes findings into a formal `Diagnosis` object containing:
  * Root cause identification.
  * Confidence score ($0.0 - 1.0$).
  * Cited `evidence_ids`.
  * Risk level classification (`LOW`, `MEDIUM`, `HIGH`).

### 5.4 Controlled Action Execution
* Tool registry supporting allowlisted operations:
  * `reset_vpn_session(user_id)`
  * `flush_dns_cache(user_id)`
  * `restart_local_service(service_name)`
  * `create_jira_escalation_ticket(summary, priority, notes)`
  * `run_health_verification(check_type, target)`
* Actions classified as `MEDIUM` or `HIGH` risk trigger an interactive `AWAITING_APPROVAL` state requiring operator confirmation.

### 5.5 Verification Engine
* Triggers verification probes post-execution (e.g., `ping_vpn_gateway`, `check_port_open`, `verify_auth_token`).
* If verification succeeds $\rightarrow$ Transitions to `RESOLVED`.
* If verification fails $\rightarrow$ Transitions to `ESCALATED` with full diagnostics attached.

---

## 6. User Flows

### 6.1 Flow A: Autonomous Low-Risk Resolution (e.g., VPN Session Glitch)
```
Employee inputs "VPN disconnected and won't reconnect"
  → Triage categorizes as Network/VPN (P3)
  → Investigation discovers stale session in gateway logs + matching KB article
  → Diagnosis: Stale VPN session lock (Confidence: 0.92, Risk: LOW)
  → Action Planner selects: reset_vpn_session
  → System executes reset_vpn_session
  → Verification probes gateway connection → Success
  → Incident resolved with explanation and evidence drawer
```

### 6.2 Flow B: High-Risk Action Requiring Approval (e.g., Production Service Restart)
```
Employee inputs "Local auth proxy service is dead"
  → Triage & Investigation diagnose service crash
  → Action Planner selects: restart_local_service (Risk: MEDIUM/HIGH)
  → State enters AWAITING_APPROVAL
  → Operator views Incident Workspace, reviews evidence, clicks "Approve"
  → Action executes → Verification verifies service running → Incident resolved
```

### 6.3 Flow C: Ambiguous or Failed Case (Escalation)
```
Employee inputs "Weird blue screen error with code 0x88F2"
  → Investigation finds no conclusive KB or duplicate tickets (Confidence: 0.35)
  → Escalation Agent compiles diagnostic brief with logs
  → Creates escalation ticket and assigns to Tier 2 Hardware Support
  → UI displays escalation status and handover summary
```

---

## 7. Non-Functional Requirements

* **Responsiveness:** Triage and initial investigation response rendered in $< 3$ seconds.
* **Auditability:** Every tool invocation, parameter payload, LLM prompt token set, and state change logged with ISO timestamps.
* **Deterministic Safety:** Hardcoded tool execution controller outside of LLM reasoning preventing unauthorized function execution.
* **Usability:** Clean, intuitive UI with clear visual indicators for agent states (Thinking, Investigating, Awaiting Approval, Verifying, Resolved).

---

## 8. MVP Scope vs. Future Scope

| Dimension | Hackathon MVP Scope | Future Enterprise Scope |
| :--- | :--- | :--- |
| **Tool Execution** | In-memory simulated IT tools with realistic state effects | Real MDM, Active Directory, and Cloud APIs (Okta, Jamf, Intune) |
| **Knowledge Base** | In-memory / SQLite vector and keyword index | Enterprise vector DB (Pinecone / BigQuery Vector Search / Milvus) |
| **ITSM Integration** | Local mock ticket database & escalation records | Bi-directional ServiceNow, Jira Service Management, Zendesk APIs |
| **Authentication** | Role-based selector (Employee vs. IT Admin) | SSO / SAML / OAuth 2.0 / OIDC with Okta / Google Workspace |
| **Telemetry** | Simulated service health endpoints | Datadog, Dynatrace, CloudWatch real-time webhooks |

---

## 9. Acceptance Criteria

1. **Intake to Completion:** An end-to-end incident flow executes without runtime crash across all 3 primary demo scenarios.
2. **Evidence Traceability:** The UI displays at least 2 distinct evidence items backing every automated diagnosis.
3. **Approval Gate Enforcement:** No medium/high risk action executes autonomously without triggering and passing the approval gate.
4. **Verification Requirement:** The state machine never marks an incident `RESOLVED` without an active verification step passing.
5. **Human Escalation Handover:** Escalated incidents produce a structured handover summary containing triage metadata and investigation findings.
