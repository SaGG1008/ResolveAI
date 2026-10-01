# ResolveAI --- UI/UX Specification

**Version:** 1.0\
**Project:** AI IT Service Desk Autonomous Resolution Agent

## 1. Design Objective

ResolveAI should look and behave like a modern enterprise AI operations
platform rather than a generic chatbot.

The UI must make the agentic process visible:

**Understand → Investigate → Decide → Act → Verify → Resolve/Escalate**

The interface should prioritize clarity, operational status, evidence,
and trust.

------------------------------------------------------------------------

# 2. Design Principles

## 2.1 Agent-First

The UI should visibly communicate which agent is active and what stage
the incident is in.

## 2.2 Evidence-First

Important decisions should be accompanied by evidence.

## 2.3 Action-Oriented

The user should always understand: - what is happening, - what action is
proposed, - whether approval is required, - what happened after
execution.

## 2.4 Controlled Autonomy

Automation should look powerful but bounded.

## 2.5 Enterprise Clarity

Avoid excessive decorative elements. The product should feel like an
operational control center.

------------------------------------------------------------------------

# 3. Visual Direction

### Overall Style

-   Premium enterprise AI
-   Dark modern interface
-   High contrast
-   Subtle futuristic elements
-   Strong typography
-   Compact information cards
-   Clear status indicators

Avoid: - excessive glassmorphism, - excessive gradients, - noisy
animations, - unnecessary illustrations, - chatbot-style conversation
bubbles as the primary interface.

------------------------------------------------------------------------

# 4. Information Hierarchy

The most important information is:

1.  Incident status
2.  Current agent
3.  Diagnosis
4.  Evidence
5.  Selected action
6.  Approval state
7.  Verification
8.  Final resolution/escalation

------------------------------------------------------------------------

# 5. Application Navigation

Sidebar:

``` text
RESOLVEAI

◉ Dashboard
▣ Incidents
◈ AI Investigations
▤ Knowledge Base
◌ System Status
▥ Analytics
⚙ Settings
```

The sidebar should remain compact and visually secondary to the incident
workspace.

------------------------------------------------------------------------

# 6. Dashboard

## Header

``` text
Good evening
AI Service Operations

[ + New Incident ]
```

## KPI Cards

``` text
ACTIVE INCIDENTS     AI RESOLUTIONS     ESCALATIONS
       12                  47                 5
```

Use simple numbers and status context.

## Recent Incidents

Columns:

``` text
Incident
Issue
Priority
AI Status
Agent
Updated
```

Example:

``` text
INC-1042
VPN Connection
Medium
Resolving
Action Planner
12 sec ago
```

------------------------------------------------------------------------

# 7. New Incident Experience

Primary input:

``` text
Describe your IT problem...

Example:
"My VPN stopped working this morning."

[ Investigate ]
```

After submission, immediately show:

``` text
Incident created: INC-1042

AI investigation started...
```

Do not leave the user on a blank loading screen.

------------------------------------------------------------------------

# 8. Incident Workspace

Recommended layout:

``` text
┌─────────────────────────────────────────────────────┐
│ INC-1042     VPN Connection Failure       RESOLVED │
├───────────────────────┬─────────────────────────────┤
│ Agent Activity        │ Incident Overview           │
│                       │                             │
│ ✓ Triage              │ Issue                       │
│ ✓ Investigation      │ Diagnosis                   │
│ ✓ Diagnosis           │ Evidence                    │
│ ✓ Action Planner      │ Selected Action             │
│ ✓ Verification       │ Verification                │
│                       │                             │
└───────────────────────┴─────────────────────────────┘
```

------------------------------------------------------------------------

# 9. Agent Activity Component

Use a vertical timeline.

``` text
✓ Triage Agent
  Classified VPN issue

✓ Investigation Agent
  Found 4 evidence sources

✓ Diagnosis Agent
  Identified expired token

→ Action Planner
  Selecting remediation...

○ Verification Agent
  Waiting
```

States:

-   `completed`
-   `active`
-   `waiting`
-   `failed`
-   `escalated`

------------------------------------------------------------------------

# 10. Evidence Component

Evidence should be displayed as compact cards.

``` text
EVIDENCE

[KB] KB-104
VPN Authentication Troubleshooting
Relevant

[TICKET] INC-421
Similar incident
Resolved by token reset

[STATUS] VPN
Infrastructure operational

[PROCEDURE] VPN-07
Token reset approved
```

Clicking evidence can expand details.

------------------------------------------------------------------------

# 11. Diagnosis Component

``` text
LIKELY CAUSE

Expired VPN authentication token

Confidence
91%

Supporting Evidence
✓ KB-104
✓ INC-421
✓ VPN Status

Uncertainty
No material conflicting evidence found.
```

Do not imply that confidence is a statistical probability unless the
implementation actually defines it that way. Label it as an AI
confidence indicator.

------------------------------------------------------------------------

# 12. Action Component

The selected action should be visually prominent.

``` text
RECOMMENDED ACTION

Reset VPN Authentication Token

Risk
LOW

Approval
PRE-APPROVED

Why?
Authentication evidence matches
the approved VPN token-reset procedure.

[ Execute Action ]
```

------------------------------------------------------------------------

# 13. Human Approval Modal

For sensitive actions:

``` text
HUMAN APPROVAL REQUIRED

Action
Disable Employee Account

Risk
HIGH

Reason
Security-sensitive operation requires
human review.

Evidence
• Security alert detected
• Account anomaly found

[ Approve ] [ Reject ] [ Escalate ]
```

The modal should clearly explain why approval is required.

------------------------------------------------------------------------

# 14. Execution Timeline

After execution:

``` text
ACTION EXECUTION

✓ Request accepted
✓ Token invalidated
✓ New token generated
→ Verifying connection...
```

Use live status where possible.

------------------------------------------------------------------------

# 15. Resolution State

``` text
✓ INCIDENT RESOLVED

VPN authentication restored.

Cause
Expired authentication token

Action
VPN token reset

Verification
Connection successfully restored

Resolution time
18 seconds

[ View Investigation ]
```

------------------------------------------------------------------------

# 16. Escalation State

``` text
⚠ ESCALATED TO HUMAN

Automated resolution was not completed.

Reason
No safe approved action available.

Evidence
3 sources reviewed

Recommended Next Step
IT security review

[ View Investigation ]
```

------------------------------------------------------------------------

# 17. Status Language

Use consistent terminology.

### Processing

-   Investigating
-   Analyzing
-   Planning
-   Verifying

### Success

-   Resolved
-   Verified
-   Completed

### Attention

-   Approval Required
-   Needs Information
-   Uncertain

### Failure

-   Action Failed
-   Verification Failed
-   Escalated

Avoid ambiguous statuses such as "AI thinking."

------------------------------------------------------------------------

# 18. Motion

Animations should communicate system activity, not decorate the
interface.

Use: - subtle progress transitions, - agent state changes, - tool
execution indicators, - success transitions.

Avoid: - constant floating animations, - excessive particle effects, -
long transitions.

------------------------------------------------------------------------

# 19. Responsive Design

The primary target is desktop/laptop because the product is an IT
operations console.

Minimum considerations: - 1280px desktop, - 1440px desktop, - smaller
laptop screens.

For narrow widths: - collapse sidebar, - stack evidence and action
panels, - maintain readable agent trace.

------------------------------------------------------------------------

# 20. Accessibility

-   strong text contrast,
-   keyboard-accessible actions,
-   clear focus states,
-   status should not rely only on color,
-   icons should have labels/tooltips,
-   error messages should be explicit.

------------------------------------------------------------------------

# 21. Demo Optimization

The first 10 seconds should communicate:

``` text
THIS IS AN AI IT OPERATIONS SYSTEM
```

The next 30--60 seconds should show:

``` text
Issue
 ↓
Agents
 ↓
Evidence
 ↓
Decision
 ↓
Action
 ↓
Verification
```

The UI should make the agent trace the visual centerpiece of the demo.

------------------------------------------------------------------------

# 22. Design Principle

> **Make autonomy visible, evidence understandable, and human control
> obvious.**
