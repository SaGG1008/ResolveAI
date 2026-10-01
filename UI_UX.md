# UI_UX — Interface Specification & Design System

## ResolveAI — AI IT Service Desk Autonomous Resolution Agent

**Version:** 1.0  
**Scope:** UI/UX Architecture, Design Tokens, Visual Hierarchy, Interaction Patterns, and Current State Audit  

---

## 1. Design Principles & Goals

ResolveAI's interface is built to demystify AI decision-making. The primary UX goal is **transparency and trust**:
1. **Explainable Agent Trace:** Users and IT operators can see exactly what the agent is thinking, querying, and deciding at every step.
2. **First-Class Evidence Presentation:** Every diagnostic conclusion visually links to source evidence (KB snippets, status pings, ticket history).
3. **Clear Risk & Approval Visuals:** Dangerous actions are highlighted with distinct risk indicators, requiring explicit single-click operator approval.
4. **Clean, Modern Operational Aesthetics:** High readability, dark/light mode support, and structured card-based layouts.

---

## 2. Design System & CSS Tokens

The interface utilizes CSS variables defined in [frontend/src/index.css](file:///c:/ResolveAI/frontend/src/index.css) supporting both light and dark modes:

### 2.1 Color Tokens
| Token | Light Mode Value | Dark Mode Value | Usage |
| :--- | :--- | :--- | :--- |
| `--bg` | `#ffffff` | `#16171d` | Main page background |
| `--text` | `#6b6375` | `#9ca3af` | Secondary body text |
| `--text-h` | `#08060d` | `#f3f4f6` | Headings and high-contrast titles |
| `--border` | `#e5e4e7` | `#2e303a` | Card borders and divider lines |
| `--code-bg` | `#f4f3ec` | `#1f2028` | Code blocks, logs, tool parameters |
| `--accent` | `#aa3bff` | `#c084fc` | Brand accent and interactive highlights |
| `--accent-bg`| `rgba(170, 59, 255, 0.1)` | `rgba(192, 132, 252, 0.15)` | Active badge and selected card backgrounds |

### 2.2 Semantic Status Colors
* **Success / Resolved:** Green (`#10b981` / `rgba(16, 185, 129, 0.15)`)
* **Running / Investigating / Verifying:** Blue / Indigo (`#3b82f6` / `rgba(59, 130, 246, 0.15)`)
* **Awaiting Approval / Warning:** Amber / Orange (`#f59e0b` / `rgba(245, 158, 11, 0.15)`)
* **Escalated / Error / High Risk:** Red / Rose (`#ef4444` / `rgba(239, 68, 68, 0.15)`)

### 2.3 Typography & Spacing
* **Font Families:**
  * Sans: `system-ui, 'Segoe UI', Roboto, sans-serif`
  * Headings: `system-ui, 'Segoe UI', Roboto, sans-serif`
  * Monospace / Logs: `ui-monospace, Consolas, monospace`
* **Base Typography:** `18px / 145%` line-height with adaptive media query (`16px` on $\le 1024\text{px}$).
* **Shadows:** Smooth layered elevation shadows for floating modals and cards.

---

## 3. Screen Layouts & Component Hierarchy

```
┌────────────────────────────────────────────────────────────────────────┐
│ TOPBAR: Logo, Active Incident Badge, System Status Indicator, Role     │
├──────────────┬─────────────────────────────────────────────────────────┤
│ SIDEBAR      │ MAIN CONTENT AREA                                       │
│              │                                                         │
│ [Dashboard]  │ ┌─────────────────────────────────────────────────────┐ │
│ [Incidents]  │ │ INCIDENT HEADER: Title, ID, Status Badge, Timestamp │ │
│ [Telemetry]  │ ├──────────────────────────┬──────────────────────────┤ │
│ [Settings]   │ │ LEFT COLUMN:             │ RIGHT COLUMN:            │ │
│              │ │ Live Agent Activity      │ Incident Overview        │ │
│              │ │ Timeline & Trace Steps   │ & Evidence Drawer        │ │
│              │ │                          │                          │ │
│              │ │ - Triage Thought         │ - User Problem Details   │ │
│              │ │ - Tool Search            │ - Diagnostic Cards       │ │
│              │ │ - Approval Prompt        │ - Evidence Snippets      │ │
│              │ │ - Verification Result    │ - Action Execution Logs  │ │
│              │ └──────────────────────────┴──────────────────────────┘ │
└──────────────┴─────────────────────────────────────────────────────────┘
```

### 3.1 Primary Views
1. **Dashboard View:**
   * Metric Cards: Active Incidents, Auto-Resolved Rate, Human Escalations, Average MTTR.
   * New Incident Submission Bar: Natural language text area with "Submit & Investigate" trigger.
   * Incident Queue Table: Priority, Category, Status, Created Time, Action CTA.
2. **Incident Workspace View:**
   * Dual-panel responsive layout.
   * Left panel: Step-by-step agent trace with expand/collapse details.
   * Right panel: Grounded evidence cards with source links and diagnosis scorecards.
3. **Human Approval Modal:**
   * Pops up when status transitions to `AWAITING_APPROVAL`.
   * Shows action name, target, risk classification, parameter payload, and reasoning.
   * Clear "Approve & Execute" vs. "Reject & Escalate" actions.

---

## 4. Current Implementation State & UI Gap Analysis

### 4.1 Current Repository State (Audited)
* `frontend/` has been initialized with React 19, TypeScript, and Vite.
* `frontend/src/index.css` contains base styling variables and typography foundations.
* `frontend/src/App.tsx` contains standard initial Vite template code.

### 4.2 UI Gaps to Be Addressed (Claude UI Workstream)
1. **Layout & Navigation Framework:** Create persistent sidebar and topbar navigation frame.
2. **Dashboard Components:** Implement KPI cards, quick-intake input, and incident table.
3. **Agent Activity Timeline:** Implement animated step items with status icons (Spinner, Checkmark, Warning).
4. **Evidence Drawer / Cards:** Implement preview cards for KB articles, status checks, and historical tickets.
5. **Approval Modal:** Implement clean action confirmation dialog.
6. **State Mocking Service:** Connect components to mock incident data service so UI is immediately interactive while backend is connected.
