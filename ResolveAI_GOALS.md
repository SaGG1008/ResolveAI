# ResolveAI --- Goals

**Version:** 1.0\
**Project:** AI IT Service Desk Autonomous Resolution Agent

# 1. North Star Goal

Build a trustworthy Agentic AI IT Service Desk that can move an employee
issue from:

**Natural-Language Problem → Investigation → Evidence → Decision →
Action → Verification → Resolution/Escalation**

The system must demonstrate meaningful agentic behavior rather than
simply generating chatbot responses.

------------------------------------------------------------------------

# 2. Hackathon Goal

Deliver a reliable, polished, demo-ready MVP within approximately **3.5
hours**.

The MVP should prioritize:

1.  Agent orchestration
2.  Tool selection
3.  Evidence-backed diagnosis
4.  Safe action execution
5.  Verification
6.  Human escalation
7.  High-quality UI

------------------------------------------------------------------------

# 3. Primary Product Goals

## Goal 1 --- Understand Issues

Accept natural-language employee IT problems.

Success: - issue category identified, - intent identified, - priority
assigned.

## Goal 2 --- Investigate Automatically

Retrieve information from multiple sources.

Success: - knowledge base searched, - previous tickets searched, -
system status checked, - troubleshooting procedure retrieved.

## Goal 3 --- Make Evidence-Based Decisions

Generate a diagnosis linked to evidence.

Success: - diagnosis has supporting evidence, - uncertainty is
visible, - fabricated evidence is never used.

## Goal 4 --- Select the Right Action

Allow the agent to dynamically choose an approved tool.

Success: - action is selected based on evidence, - tool is
allowlisted, - risk/approval is checked.

## Goal 5 --- Execute Safely

Perform only approved simulated remediation.

Success: - no arbitrary execution, - failed actions are recorded as
failures, - sensitive actions require approval.

## Goal 6 --- Verify Resolution

Never declare success merely because an action was executed.

Success: - post-action verification occurs, - verified incidents become
resolved, - failed verification triggers escalation.

## Goal 7 --- Escalate Intelligently

Know when the agent should stop acting autonomously.

Success: - high-risk cases escalate, - uncertain cases escalate, -
failed remediation escalates, - evidence conflicts can trigger
escalation.

------------------------------------------------------------------------

# 4. Demo Goals

The final demo should successfully demonstrate three scenarios.

### Scenario 1 --- Automatic Resolution

VPN issue:

``` text
Issue
→ Investigate
→ Diagnose
→ Reset Token
→ Verify
→ Resolved
```

### Scenario 2 --- Another Routine Resolution

Email synchronization issue:

``` text
Issue
→ Investigate
→ Diagnose
→ Approved remediation
→ Verify
→ Resolved
```

### Scenario 3 --- Human Escalation

Security-sensitive issue:

``` text
Issue
→ Investigate
→ Risk identified
→ Human approval/escalation
```

------------------------------------------------------------------------

# 5. Technical Goals

The system should achieve:

-   modular agent architecture,
-   structured agent outputs,
-   controlled tool registry,
-   reliable state transitions,
-   evidence traceability,
-   safe tool execution,
-   verification,
-   failure handling,
-   observable agent activity.

------------------------------------------------------------------------

# 6. UX Goals

The user should always know:

1.  What issue is being investigated.
2.  Which agent is active.
3.  What evidence was found.
4.  What the system thinks the likely cause is.
5.  What action it selected.
6.  Whether approval is required.
7.  Whether the action succeeded.
8.  Whether the issue was verified.
9.  Whether the incident was resolved or escalated.

------------------------------------------------------------------------

# 7. Quality Goals

The MVP should be:

### Reliable

The three core scenarios should run repeatedly.

### Explainable

Important decisions have visible evidence.

### Safe

The LLM cannot execute arbitrary operations.

### Fast

No unnecessary infrastructure should slow down the demo.

### Understandable

A judge should understand the product without reading the source code.

------------------------------------------------------------------------

# 8. Scope Priorities

## P0 --- Must Achieve

``` text
✓ Issue intake
✓ Triage
✓ Investigation
✓ Evidence
✓ Diagnosis
✓ Action planning
✓ Tool execution
✓ Verification
✓ Escalation
✓ Agent trace
✓ Working UI
✓ Three demo scenarios
```

## P1 --- Achieve If Time Allows

``` text
○ Streaming events
○ Approval modal
○ Incident history
○ Confidence indicator
○ Action timeline
```

## P2 --- Do Not Prioritize During 3.5-Hour Build

``` text
○ Real enterprise integrations
○ Advanced analytics
○ Complex authentication
○ Production monitoring
○ Large-scale vector infrastructure
○ Mobile application
○ Enterprise deployment
```

------------------------------------------------------------------------

# 9. Success Metrics

For the hackathon MVP:

### Functional

-   3/3 demo scenarios complete successfully.
-   100% of automated resolutions are verified before being marked
    resolved.
-   0 arbitrary tool executions.
-   0 fabricated tool-success states.

### UX

-   User can submit an issue immediately.
-   Agent state is visible throughout investigation.
-   Evidence is visible before action execution.
-   Resolution/escalation state is unambiguous.

### Demo

A judge should be able to understand the core concept within one minute:

> **ResolveAI investigates IT problems and autonomously resolves
> approved issues while escalating cases that require humans.**

------------------------------------------------------------------------

# 10. Anti-Goals

ResolveAI should NOT become:

-   a generic ChatGPT wrapper,
-   a static decision tree,
-   a collection of disconnected AI features,
-   an unrestricted autonomous computer-control system,
-   a fake dashboard with hardcoded "AI" activity.

The agentic workflow must be real within the controlled prototype
environment.

------------------------------------------------------------------------

# 11. Final Goal

> **Build the smallest system that convincingly demonstrates autonomous,
> evidence-driven IT incident resolution with safe action selection,
> verification, and human escalation.**

That is the definition of success for the hackathon version of
ResolveAI.
