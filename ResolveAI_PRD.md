# PRD --- ResolveAI

## AI IT Service Desk Autonomous Resolution Agent

**Version:** 1.0\
**Status:** Hackathon MVP / Demo-Ready Prototype\
**Primary Objective:** Build a focused Agentic AI IT Service Desk that
investigates employee IT issues, selects appropriate actions, executes
approved low-risk resolutions, verifies the result, and escalates
unresolved or high-risk issues to a human.

------------------------------------------------------------------------

## 1. Product Overview

### 1.1 Product Name

**ResolveAI**

### 1.2 Product Concept

ResolveAI is an Agentic AI IT Service Desk designed around the problem
statement:

> From Employee Problem to Resolution

The system receives an employee IT issue and investigates relevant
knowledge-base information, system status, previous tickets, and
troubleshooting procedures. It then determines an appropriate resolution
or escalation path.

The defining behavior is that the agent should **select the appropriate
tool/action based on the issue rather than blindly following a fixed
workflow**.

### 1.3 Source Alignment

The source problem statement specifies the following core flow:

**Ticket Triage → Knowledge/RAG → System Diagnosis → Troubleshooting →
Resolution → Escalation**

It identifies the key challenge as appropriate tool/action selection
rather than blind execution.

For the hackathon MVP, ResolveAI implements this concept through a small
number of cooperating logical agents and safe simulated IT tools.

------------------------------------------------------------------------

# 2. Problem Statement

Employees frequently report IT problems in natural language, while the
information needed to resolve those problems is distributed across
knowledge bases, system status, historical tickets, and troubleshooting
procedures.

A conventional chatbot can provide instructions, but it does not
necessarily:

-   investigate multiple sources,
-   correlate evidence,
-   determine the likely cause,
-   select an appropriate action,
-   execute an approved action,
-   verify whether the action worked,
-   or know when to escalate to a human.

ResolveAI addresses this gap by providing an evidence-driven agentic
workflow from issue intake through resolution or escalation.

------------------------------------------------------------------------

# 3. Product Vision

Create a service-desk agent that behaves like an intelligent first-line
IT operations assistant:

**Understand → Investigate → Diagnose → Decide → Act → Verify →
Resolve/Escalate**

The system should make its investigation and action selection visible to
the user so that the demo clearly demonstrates agentic behavior rather
than presenting a generic conversational AI interface.

------------------------------------------------------------------------

# 4. Goals

## 4.1 Primary Goals

1.  Accept employee IT issues in natural language.
2.  Automatically classify and prioritize incoming issues.
3.  Investigate relevant knowledge-base information.
4.  Search previous tickets for similar incidents.
5.  Check simulated system/service status.
6.  Retrieve approved troubleshooting procedures.
7.  Generate an evidence-backed diagnosis.
8.  Select the most appropriate available action.
9.  Execute safe, approved actions.
10. Verify whether the issue was resolved.
11. Escalate when automated resolution is inappropriate or unsuccessful.
12. Show an understandable agent activity trace.
13. Show evidence supporting important decisions.
14. Produce a polished demo-ready dashboard.

## 4.2 Secondary Goals

-   Demonstrate RAG/tool usage.
-   Demonstrate multi-agent orchestration.
-   Demonstrate human-in-the-loop control.
-   Demonstrate explainability.
-   Demonstrate action verification.

------------------------------------------------------------------------

# 5. Non-Goals

The MVP will NOT attempt to:

-   administer real enterprise Windows machines,
-   connect to real corporate identity systems,
-   modify real employee accounts,
-   integrate with production ServiceNow/Jira environments,
-   monitor real enterprise infrastructure,
-   build a complete enterprise ITSM platform,
-   implement dozens of autonomous agents,
-   provide unrestricted system-level execution.

All actions in the hackathon prototype should be simulated or safely
sandboxed.

------------------------------------------------------------------------

# 6. Target Users

## 6.1 Primary User --- Employee

An employee reports an IT problem such as:

-   VPN failure
-   email synchronization issue
-   password/access problem
-   connectivity problem
-   printer issue
-   application/service failure

The employee wants a fast resolution without needing to understand
technical troubleshooting.

## 6.2 Secondary User --- IT Support Agent

The IT support agent needs to:

-   inspect the investigation,
-   understand the evidence,
-   review the proposed action,
-   approve/reject risky actions,
-   take over escalated incidents.

## 6.3 Demo/Judge User

A hackathon judge should be able to understand the system within seconds
by observing:

**Issue → Agent Investigation → Evidence → Decision → Action →
Verification → Resolution**

------------------------------------------------------------------------

# 7. Core User Journey

``` text
Employee submits issue
        ↓
Triage Agent
        ↓
Investigation Agent
        ↓
Knowledge Base / RAG
        ↓
Previous Tickets
        ↓
System Status
        ↓
Troubleshooting Procedures
        ↓
Diagnosis Agent
        ↓
Action Planner
        ↓
Risk / Approval Check
        ↓
Execute Approved Action
        ↓
Verification Agent
        ↓
   ┌───────────────┐
   │               │
Resolved        Not Resolved
   │               │
   ↓               ↓
Close          Escalate
Incident       to Human
```

------------------------------------------------------------------------

# 8. Agent Architecture

The MVP should use five logical agents.

## 8.1 Triage Agent

### Responsibility

Understand the employee's issue and classify it.

### Inputs

-   User description
-   Optional employee metadata
-   Optional incident history

### Outputs

-   Category
-   Intent
-   Priority
-   Initial investigation requirements

### Example

``` json
{
  "category": "VPN",
  "intent": "connection_failure",
  "priority": "medium",
  "requires_investigation": true
}
```

------------------------------------------------------------------------

## 8.2 Investigation Agent

### Responsibility

Collect relevant evidence from available tools.

### Tools

-   Knowledge Base Search
-   Previous Ticket Search
-   System Status Lookup
-   Troubleshooting Procedure Lookup

### Output

A structured evidence set containing:

-   relevant knowledge articles,
-   similar tickets,
-   current system status,
-   applicable procedures,
-   source identifiers.

------------------------------------------------------------------------

## 8.3 Diagnosis Agent

### Responsibility

Correlate investigation results and determine the most plausible cause.

### Requirements

The agent must distinguish:

-   observed facts,
-   evidence-supported conclusions,
-   uncertainty.

### Example

``` text
Likely Cause:
Expired VPN authentication token

Evidence:
- VPN infrastructure operational
- Similar historical incident found
- KB procedure matches observed symptoms

Confidence:
91%
```

------------------------------------------------------------------------

## 8.4 Action Planner Agent

### Responsibility

Select the most appropriate available action.

### Possible Actions

-   Reset VPN token
-   Restart approved service
-   Clear DNS cache
-   Create ticket
-   Request additional information
-   Escalate to human

### Requirements

The agent must:

1.  Consider available evidence.
2.  Consider available actions.
3.  Check whether the action is approved.
4.  Prefer the least risky valid action.
5.  Explain why the action was selected.
6.  Avoid unsupported actions.

------------------------------------------------------------------------

## 8.5 Verification & Escalation Agent

### Responsibility

Determine whether the selected action actually resolved the incident.

### Flow

``` text
Execute Action
     ↓
Verify Result
     ↓
Success?
 ┌───┴───┐
Yes      No
 ↓        ↓
Resolve  Escalate
```

The agent should also escalate when:

-   no safe automated action exists,
-   evidence is contradictory,
-   confidence is insufficient,
-   the action requires human approval,
-   automated remediation fails.

------------------------------------------------------------------------

# 9. Tool Layer

The tool layer provides controlled capabilities to the agents.

## 9.1 Knowledge Base Search

`search_knowledge_base(query)`

Returns relevant troubleshooting articles.

## 9.2 Previous Ticket Search

`search_previous_tickets(query)`

Returns similar historical incidents.

## 9.3 System Status

`get_system_status(service)`

Returns the current simulated health/status of a service.

## 9.4 Troubleshooting Procedure

`get_troubleshooting_procedure(issue_type)`

Returns approved procedures and their permitted actions.

## 9.5 Remediation Tools

Examples:

-   `reset_vpn_token()`
-   `restart_service(service)`
-   `clear_dns_cache()`

These should be simulated in the MVP.

## 9.6 Ticket Creation

`create_ticket(summary, evidence, priority)`

Creates a simulated incident record.

## 9.7 Escalation

`escalate_to_human(reason, evidence)`

Transfers the incident to human IT support.

## 9.8 Resolution Verification

`verify_resolution(issue_type)`

Checks the simulated post-action state.

------------------------------------------------------------------------

# 10. Data Model

The prototype can use JSON or SQLite.

## 10.1 Knowledge Base

Fields:

-   id
-   title
-   category
-   symptoms
-   solution
-   approved_actions
-   source

## 10.2 Tickets

Fields:

-   ticket_id
-   user
-   category
-   description
-   status
-   resolution
-   created_at
-   resolved_at

## 10.3 System Status

Fields:

-   service
-   status
-   last_checked
-   active_incidents

## 10.4 Procedures

Fields:

-   procedure_id
-   issue_type
-   steps
-   approved_actions
-   risk_level
-   requires_human_approval

## 10.5 Incident

Fields:

-   incident_id
-   user
-   description
-   category
-   priority
-   agent_status
-   evidence
-   diagnosis
-   selected_action
-   action_result
-   verification_result
-   final_status

------------------------------------------------------------------------

# 11. UI/UX Requirements

## 11.1 Dashboard

The dashboard should show:

-   Active Incidents
-   AI Resolutions
-   Escalations
-   Recent Incidents
-   Agent Activity

Example:

``` text
ACTIVE INCIDENTS     AI RESOLUTIONS     ESCALATIONS
      12                   47                5
```

## 11.2 New Issue Panel

Provide a prominent input:

``` text
Describe your IT problem...

[ Investigate ]
```

The interaction should feel conversational but operational rather than
like a generic chatbot.

## 11.3 Agent Activity Trace

Display agent states:

``` text
✓ Triage Agent
✓ Investigation Agent
✓ Diagnosis Agent
→ Action Planner
○ Verification Agent
```

The active agent should be visually distinguishable.

## 11.4 Evidence Panel

Show evidence supporting the diagnosis:

``` text
EVIDENCE

✓ KB-104 — VPN Authentication
✓ Ticket #421 — Similar Incident
✓ VPN Status — Operational
✓ Procedure VPN-07 — Token Reset
```

## 11.5 Action Panel

Show:

-   selected action,
-   reason,
-   risk,
-   approval requirement,
-   execute button.

Example:

``` text
SELECTED ACTION

Reset VPN Authentication Token

Risk: Low
Approval: Pre-approved

[ Execute Action ]
```

## 11.6 Resolution Screen

Show:

-   final status,
-   root cause,
-   action taken,
-   verification result,
-   resolution time,
-   evidence.

------------------------------------------------------------------------

# 12. Explainability Requirements

Every major agent decision should be traceable.

For an automated action, show:

### Why this action?

``` text
Selected:
Reset VPN Token

Evidence:
✓ VPN infrastructure is operational
✓ Authentication failure detected
✓ Similar historical incident found
✓ Approved token-reset procedure exists

Rejected:
Restart VPN Service
Reason: Service is operational

Rejected:
Human Escalation
Reason: Safe approved automated resolution exists
```

The UI should make clear that these are evidence-backed system
decisions, not hidden reasoning.

------------------------------------------------------------------------

# 13. Human-in-the-Loop

The MVP must support escalation and approval.

### Low-Risk Action

``` text
Reset VPN Token
→ Automatically executable
```

### High-Risk Action

``` text
Disable Employee Account
→ Human approval required
```

Approval UI:

``` text
HUMAN APPROVAL REQUIRED

Action:
Disable Account

Reason:
Potential security incident

[ Approve ] [ Reject ] [ Escalate ]
```

------------------------------------------------------------------------

# 14. Example Demo Scenarios

## Scenario A --- VPN Auto Resolution

### Input

"My VPN stopped working this morning."

### Expected Flow

1.  Triage → VPN / Authentication
2.  Search KB
3.  Search previous tickets
4.  Check VPN status
5.  Retrieve troubleshooting procedure
6.  Diagnose expired token
7.  Select reset-token action
8.  Execute simulated reset
9.  Verify connection
10. Mark resolved

### Expected Result

``` text
RESOLVED ✓

Cause:
Expired authentication token

Action:
VPN token reset

Verification:
Connection restored
```

------------------------------------------------------------------------

## Scenario B --- Email Service Issue

### Input

"My company email is not syncing."

### Expected Flow

1.  Classify email issue.
2.  Search KB.
3.  Check email service status.
4.  Search similar incidents.
5.  Retrieve approved restart/sync procedure.
6.  Select appropriate action.
7.  Execute simulated action.
8.  Verify synchronization.
9.  Resolve.

------------------------------------------------------------------------

## Scenario C --- High-Risk Security Issue

### Input

"I think someone accessed my account."

### Expected Flow

1.  Triage as security-sensitive.
2.  Search relevant procedures.
3.  Investigate available evidence.
4.  Identify that automated account modification requires human
    approval.
5.  Create incident.
6.  Escalate.
7.  Display evidence and reason for escalation.

### Expected Result

``` text
ESCALATED TO HUMAN

Reason:
Security-sensitive action requires human review.

Evidence:
...
```

------------------------------------------------------------------------

# 15. Functional Requirements

## FR-01 --- Issue Intake

The system shall accept a natural-language IT issue.

## FR-02 --- Issue Classification

The system shall classify the issue category and priority.

## FR-03 --- Evidence Retrieval

The system shall retrieve relevant knowledge-base information.

## FR-04 --- Historical Investigation

The system shall search previous tickets for similar incidents.

## FR-05 --- System Diagnosis

The system shall retrieve simulated service/system status.

## FR-06 --- Procedure Retrieval

The system shall retrieve relevant approved troubleshooting procedures.

## FR-07 --- Evidence-Based Diagnosis

The system shall produce a diagnosis supported by retrieved evidence.

## FR-08 --- Action Selection

The system shall select an appropriate available action.

## FR-09 --- Action Explanation

The system shall explain the evidence supporting the selected action.

## FR-10 --- Safe Execution

The system shall execute only approved simulated actions.

## FR-11 --- Verification

The system shall verify the result after remediation.

## FR-12 --- Escalation

The system shall escalate unresolved or high-risk incidents to a human.

## FR-13 --- Agent Trace

The system shall display the current and completed agent stages.

## FR-14 --- Incident Record

The system shall store the investigation and final incident status.

------------------------------------------------------------------------

# 16. Non-Functional Requirements

## Performance

-   Initial triage should return quickly.
-   Tool calls should provide visible progress states.
-   The demo should avoid long unexplained loading periods.

## Reliability

-   Tool failures must be handled gracefully.
-   Failed actions must not be presented as successful.
-   The system must be able to fall back to escalation.

## Safety

-   Real destructive system actions are prohibited in the MVP.
-   High-risk actions require human approval.
-   Agents must not invent tool results.
-   Evidence should be distinguishable from generated conclusions.

## Explainability

-   Important decisions must expose supporting evidence.
-   The system should clearly identify uncertainty.

## Usability

-   The main incident state should be understandable at a glance.
-   Agent activity should be visible.
-   Resolution and escalation states should be unambiguous.

------------------------------------------------------------------------

# 17. MVP Scope

The minimum demo-ready implementation must contain:

### Must Have

-   Natural-language issue intake
-   Triage agent
-   Investigation agent
-   Knowledge-base search
-   Previous-ticket search
-   System-status lookup
-   Diagnosis
-   Action planning
-   At least 3 simulated remediation tools
-   Verification
-   Human escalation
-   Agent activity trace
-   Evidence display
-   Dashboard
-   At least 3 working demo scenarios

### Should Have

-   RAG retrieval
-   Confidence indicator
-   Human approval modal
-   Incident history
-   Action timeline

### Could Have

-   Analytics
-   Advanced search
-   Multiple user roles
-   Real ticketing integrations
-   Real infrastructure integrations

------------------------------------------------------------------------

# 18. Success Criteria

The MVP is successful if a judge can observe a complete flow:

``` text
Natural-Language Issue
        ↓
Agent Investigation
        ↓
Multiple Evidence Sources
        ↓
Diagnosis
        ↓
Dynamic Action Selection
        ↓
Tool Execution
        ↓
Verification
        ↓
Resolution / Escalation
```

The demo should clearly show that the system is not simply generating a
textual answer.

------------------------------------------------------------------------

# 19. Hackathon Delivery Plan --- 3.5 Hours

## Phase 1 --- 0:00--0:20

Project setup and architecture.

Deliverables: - repository structure - agent interfaces - tool
interfaces - data schemas

## Phase 2 --- 0:20--1:10

Implement agent orchestration.

Deliverables: - Triage - Investigation - Diagnosis - Action Planning -
Verification

## Phase 3 --- 1:10--1:40

Create controlled datasets and tools.

Deliverables: - knowledge base - tickets - system status - procedures -
simulated actions

## Phase 4 --- 1:40--2:40

Build UI.

Deliverables: - dashboard - issue intake - agent trace - evidence
panel - action panel - resolution/escalation state

## Phase 5 --- 2:40--3:05

Integrate frontend and backend.

## Phase 6 --- 3:05--3:25

Polish and test the three demo scenarios.

## Phase 7 --- 3:25--3:30

Freeze features and prepare final demonstration.

------------------------------------------------------------------------

# 20. Demo Narrative

The recommended presentation should follow one incident from beginning
to end.

### Opening

> "Instead of simply answering an employee's IT question, ResolveAI
> investigates the issue, decides what action is appropriate, executes
> an approved resolution, verifies the result, and escalates when
> automation is unsafe."

### Live Demo

1.  Submit VPN issue.
2.  Show Triage Agent.
3.  Show Knowledge Base retrieval.
4.  Show previous ticket retrieval.
5.  Show system status.
6.  Show diagnosis.
7.  Show action selection.
8.  Execute action.
9.  Show verification.
10. Show resolution.
11. Briefly demonstrate a second high-risk issue that gets escalated.

### Closing

Show:

``` text
UNDERSTAND
     ↓
INVESTIGATE
     ↓
DECIDE
     ↓
ACT
     ↓
VERIFY
     ↓
RESOLVE / ESCALATE
```

------------------------------------------------------------------------

# 21. Technical Boundaries

The prototype should prioritize:

**Agent behavior \> integrations \> feature count**

The implementation should prefer controlled simulated enterprise data
over spending the limited build window on production integrations.

The system should demonstrate genuine agentic decision-making while
keeping execution safe and deterministic enough for a reliable hackathon
demonstration.

------------------------------------------------------------------------

# 22. Product Definition of Done

ResolveAI is considered demo-ready when:

-   [ ] Employee can submit an IT issue.
-   [ ] Triage agent classifies the issue.
-   [ ] Investigation retrieves evidence from at least three sources.
-   [ ] Diagnosis references evidence.
-   [ ] Action planner selects an appropriate tool.
-   [ ] At least one low-risk action executes automatically.
-   [ ] Action result is verified.
-   [ ] Failed/unsafe cases escalate.
-   [ ] Agent activity is visible.
-   [ ] Evidence is visible.
-   [ ] Incident state is stored.
-   [ ] Three demo scenarios work end-to-end.
-   [ ] No fake successful execution is shown when a tool fails.
-   [ ] UI clearly communicates Resolved vs Escalated.
-   [ ] The final demo can be completed without manual backend
    intervention.

------------------------------------------------------------------------

# 23. Future Expansion

After the hackathon MVP, ResolveAI could expand toward:

-   real ITSM integrations,
-   enterprise identity integration,
-   real monitoring systems,
-   endpoint management,
-   Slack/Teams service desk interfaces,
-   role-based access control,
-   persistent incident memory,
-   richer RAG,
-   automated runbooks,
-   approval policies,
-   audit logs,
-   organization-specific agents.

These are explicitly outside the 3.5-hour MVP scope.

------------------------------------------------------------------------

# 24. Final Product Principle

> **ResolveAI should not merely tell employees how to fix an IT problem.
> It should investigate the problem, select an appropriate action,
> safely execute what it is authorized to do, verify the outcome, and
> know when to hand control to a human.**

That principle defines the MVP.
