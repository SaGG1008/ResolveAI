# AGENT_RULES — AI Agent Engineering & Runtime Guardrails

## ResolveAI — AI IT Service Desk Autonomous Resolution Agent

**Version:** 1.0  
**Scope:** Strict operational guidelines for both **(1) AI Coding Agents (Developers)** working on this repository, and **(2) AI Domain Agents (Runtime)** executing incident resolution workflows.

---

# PART 1: Rules for AI Coding Agents (Developers & Contributors)

### 1. Collaboration & UI Preservation (CRITICAL)
* **Claude UI Lane:** Claude is actively working on the frontend UI/UX implementation. **DO NOT** redesign, rewrite, replace, or modify the UI components created by Claude unless explicitly instructed by the user.
* **No Duplicate Components:** Reuse existing components in `frontend/src/components/`. Do not create parallel or competing implementations.

### 2. Code Modification Standards
* **Inspect First:** Always read and inspect existing files before attempting edits. Never make assumptions about signatures or file structures.
* **Minimal & Surgical Edits:** Keep code changes focused and minimal. Do not rewrite entire files when editing a specific function or block.
* **Maintain Documentation Integrity:** Preserve all existing comments, docstrings, and architectural diagrams.
* **Follow Architecture:** Adhere strictly to the layers defined in [ARCHITECTURE.md](file:///c:/ResolveAI/ARCHITECTURE.md).

### 3. Engineering & Safety Invariants
* **Type Safety:** Maintain strict TypeScript interfaces (`frontend/src/types/`) and Python Pydantic models (`backend/app/models/`). No untyped `any` or loose dictionaries in core APIs.
* **Zero Hardcoded Secrets:** Never commit real API keys, passwords, or tokens. Use environment variables defined in [ENVIRONMENT.md](file:///c:/ResolveAI/ENVIRONMENT.md).
* **Dependency Hygiene:** Do not install unnecessary packages. Check existing `package.json` and `requirements.txt` before adding dependencies.
* **Error Resilience:** Wrap network and LLM calls in structured try/catch/except handlers with fallback behaviors. Never leave unhandled promise rejections or uncaught exceptions.
* **MVP & Hackathon Focus:** Prioritize demo stability and core functionality over complex premature optimizations.

---

# PART 2: Rules for AI Domain Agents (Runtime Incident Resolution)

These rules govern the autonomous runtime behavior of ResolveAI agents inside the service desk engine.

```
┌─────────────────────────────────────────────────────────────┐
│                 CORE RUNTIME INVARIANT                      │
│ The agent may reason and select from approved capabilities, │
│ but application code controls what the agent executes.      │
└─────────────────────────────────────────────────────────────┘
```

### 1. Evidence Before Action
* The agent must never select a remediation action without linking it to verified evidence gathered during investigation.
* Speculative or ungrounded actions are strictly prohibited.

### 2. No Fabricated Evidence or Hallucinated Data
* If information is missing from the Knowledge Base or telemetry feeds, the agent must acknowledge the information gap.
* Tool results must reflect real execution returns; failed tool executions must never be disguised as successes.

### 3. Separation of Facts vs. Conclusions
* Retrieved data (KB snippets, system pings, past tickets) are treated as immutable **Facts (Evidence)**.
* Root cause analyses, hypotheses, and confidence metrics are treated as **Conclusions (Diagnosis)**.

### 4. Least-Risk Action Selection
* When multiple remediation paths are available, the agent must select the action with the lowest blast radius (e.g., DNS flush before full service reboot).

### 5. Mandatory Human Approval Gates
* Any action classified as `MEDIUM` or `HIGH` risk must pause in the `AWAITING_APPROVAL` state.
* The system must never execute elevated actions without an explicit confirmation from an authorized user/operator.

### 6. Mandatory Post-Action Verification
* An incident must never transition to `RESOLVED` purely because an action executed with exit code 0.
* A dedicated verification probe (e.g., ping test, connectivity check, status query) must confirm that the underlying issue is genuinely resolved.

### 7. Explicit Escalation Triggers
The agent must immediately halt autonomous remediation and trigger Tier-2 human escalation under any of the following conditions:
1. Diagnosis confidence is below threshold ($< 0.70$).
2. Conflicting evidence is detected across data sources.
3. Remediation tool execution fails or errors out.
4. Post-action verification fails.
5. The required action is classified as high-risk and is rejected by the human approver.

### 8. Strict Tool Allowlisting & Sandboxing
* Agents are restricted to tools registered in `backend/app/tools/registry.py`.
* Agents cannot execute arbitrary bash/shell commands, dynamic Python code, or unapproved network requests.

### 9. Complete Auditability & Traceability
* Every prompt, thought step, tool invocation, parameter payload, and decision rationale must be recorded in the `agent_traces` audit log.
