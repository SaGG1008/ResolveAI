# API — Backend REST & Streaming API Specification

## ResolveAI — AI IT Service Desk Autonomous Resolution Agent

**Version:** 1.0  
**Base URL:** `http://localhost:8000/api`  
**Protocol:** HTTP/1.1 REST + Server-Sent Events (SSE)  

---

## 1. Overview & Response Format

All standard JSON REST endpoints return payloads structured as:
```json
{
  "success": true,
  "data": {},
  "error": null
}
```
In case of errors:
```json
{
  "success": false,
  "data": null,
  "error": {
    "code": "INVALID_STATE_TRANSITION",
    "message": "Cannot execute action while in INVESTIGATING state."
  }
}
```

---

## 2. Endpoints Specification

### 2.1 Create Incident
* **Endpoint:** `/incidents`
* **Method:** `POST`
* **Authentication:** Optional for MVP / Bearer Token in production
* **Purpose:** Submit a new natural language IT issue for triage and autonomous resolution.
* **Request Body:**
  ```json
  {
    "description": "My VPN keeps dropping every 5 minutes and says authentication session expired.",
    "user_id": "usr_9482",
    "user_name": "Sarah Connor",
    "user_email": "sarah.connor@enterprise.io",
    "device_info": {
      "os": "macOS 15.1",
      "ip": "10.14.22.8"
    }
  }
  ```
* **Response Body (`201 Created`):**
  ```json
  {
    "success": true,
    "data": {
      "id": "inc_7f8a12bc",
      "title": "VPN Session Authentication Glitch",
      "description": "My VPN keeps dropping every 5 minutes and says authentication session expired.",
      "category": "Network / VPN",
      "priority": "P3",
      "status": "RECEIVED",
      "created_at": "2026-10-01T09:42:00Z",
      "updated_at": "2026-10-01T09:42:00Z"
    },
    "error": null
  }
  ```
* **Error Responses:**
  * `400 Bad Request`: Validation failure on empty or oversized description.

---

### 2.2 List Incidents
* **Endpoint:** `/incidents`
* **Method:** `GET`
* **Authentication:** None
* **Purpose:** Retrieve a list of recent incidents for the dashboard view.
* **Query Parameters:**
  * `status` (optional): Filter by incident status (e.g. `RESOLVED`, `AWAITING_APPROVAL`).
  * `limit` (optional, default: 20): Maximum number of items.
* **Response Body (`200 OK`):**
  ```json
  {
    "success": true,
    "data": {
      "incidents": [
        {
          "id": "inc_7f8a12bc",
          "title": "VPN Session Disconnect",
          "category": "Network / VPN",
          "priority": "P3",
          "status": "RESOLVED",
          "user_name": "Sarah Connor",
          "created_at": "2026-10-01T09:42:00Z",
          "resolution_time_seconds": 14
        }
      ],
      "total": 1
    },
    "error": null
  }
  ```

---

### 2.3 Get Incident Details & Evidence
* **Endpoint:** `/incidents/{incident_id}`
* **Method:** `GET`
* **Authentication:** None
* **Purpose:** Retrieve full state, diagnosis, evidence items, and trace logs for a specific incident.
* **Response Body (`200 OK`):**
  ```json
  {
    "success": true,
    "data": {
      "id": "inc_7f8a12bc",
      "title": "VPN Session Authentication Glitch",
      "description": "My VPN keeps dropping every 5 minutes...",
      "status": "RESOLVED",
      "category": "Network / VPN",
      "priority": "P3",
      "diagnosis": {
        "root_cause": "Stale gateway session lock preventing continuous handshake.",
        "confidence": 0.94,
        "risk_level": "LOW",
        "cited_evidence_ids": ["ev_101", "ev_102"]
      },
      "evidence": [
        {
          "id": "ev_101",
          "source_type": "TELEMETRY",
          "title": "VPN Gateway Session Table",
          "snippet": "Session usr_9482 flagged as STALE_LOCK on gw-us-east-1.",
          "relevance_score": 0.98
        },
        {
          "id": "ev_102",
          "source_type": "KNOWLEDGE_BASE",
          "title": "KB-402: Resolving Stale VPN Session Locks",
          "snippet": "Run session reset to clear dead gateway tokens.",
          "relevance_score": 0.91
        }
      ],
      "traces": [
        {
          "id": "tr_1",
          "agent_name": "TriageAgent",
          "step_type": "THOUGHT",
          "content": "Classified issue as Network/VPN priority P3.",
          "status": "COMPLETED",
          "timestamp": "2026-10-01T09:42:01Z"
        }
      ],
      "action": {
        "tool_name": "reset_vpn_session",
        "risk_level": "LOW",
        "requires_approval": false,
        "execution_status": "SUCCESS"
      },
      "verification": {
        "is_verified": true,
        "probe_type": "GATEWAY_HANDSHAKE_PROBE",
        "result_message": "Gateway handshake returned active status 200 OK."
      }
    },
    "error": null
  }
  ```
* **Error Responses:**
  * `404 Not Found`: Incident does not exist.

---

### 2.4 Trigger Incident Investigation
* **Endpoint:** `/incidents/{incident_id}/investigate`
* **Method:** `POST`
* **Authentication:** None
* **Purpose:** Start or resume autonomous multi-agent resolution for an incident.
* **Response Body (`202 Accepted`):**
  ```json
  {
    "success": true,
    "data": {
      "incident_id": "inc_7f8a12bc",
      "status": "INVESTIGATING",
      "message": "Investigation pipeline dispatched."
    },
    "error": null
  }
  ```

---

### 2.5 Submit Action Approval
* **Endpoint:** `/incidents/{incident_id}/approval`
* **Method:** `POST`
* **Authentication:** Required in production (Operator role)
* **Purpose:** Approve or reject an elevated action when the incident is in `AWAITING_APPROVAL`.
* **Request Body:**
  ```json
  {
    "approved": true,
    "operator_id": "admin_44",
    "operator_notes": "Approved restart during standard working hours."
  }
  ```
* **Response Body (`200 OK`):**
  ```json
  {
    "success": true,
    "data": {
      "incident_id": "inc_7f8a12bc",
      "status": "EXECUTING",
      "message": "Action approved. Resuming execution."
    },
    "error": null
  }
  ```
* **Error Responses:**
  * `400 Bad Request`: Incident is not currently awaiting approval.

---

### 2.6 Real-Time Event Stream (Server-Sent Events)
* **Endpoint:** `/incidents/{incident_id}/stream`
* **Method:** `GET`
* **Protocol:** `text/event-stream`
* **Purpose:** Provides a persistent live event stream delivering trace events, evidence discoveries, and state transitions to the UI.
* **Event Payload Structure:**
  ```text
  event: trace_event
  data: {"incident_id": "inc_7f8a12bc", "agent": "InvestigationAgent", "thought": "Querying VPN telemetry logs...", "status": "IN_PROGRESS", "timestamp": "2026-10-01T09:42:03Z"}

  event: evidence_discovered
  data: {"id": "ev_101", "source_type": "TELEMETRY", "title": "VPN Gateway Session Table", "snippet": "Session usr_9482 flagged as STALE_LOCK", "relevance_score": 0.98}

  event: state_changed
  data: {"incident_id": "inc_7f8a12bc", "old_state": "INVESTIGATING", "new_state": "DIAGNOSING"}
  ```

---

### 2.7 System Status & Health
* **Endpoint:** `/system/status`
* **Method:** `GET`
* **Purpose:** Health check endpoint returning backend uptime and simulated enterprise service health (VPN Gateway, Identity Provider, Mail Cluster).
* **Response Body (`200 OK`):**
  ```json
  {
    "success": true,
    "data": {
      "backend_status": "HEALTHY",
      "services": [
        { "name": "VPN Gateway (US-East)", "status": "OPERATIONAL", "latency_ms": 28 },
        { "name": "Okta SSO Provider", "status": "OPERATIONAL", "latency_ms": 45 },
        { "name": "Internal Git Proxy", "status": "DEGRADED", "latency_ms": 410 }
      ]
    },
    "error": null
  }
  ```

---

## 3. Tool Registry Endpoints

### 3.1 List All Tools
* **Endpoint:** `/tools`
* **Method:** `GET`
* **Purpose:** Retrieve a list of all available tools in the registry.
* **Response Body (`200 OK`):**
  ```json
  [
    {
      "name": "search_knowledge_base",
      "description": "Search the knowledge base for relevant articles and procedures",
      "risk_level": "low",
      "approval_required": false
    },
    {
      "name": "reset_vpn_token",
      "description": "Reset user VPN token to resolve authentication issues",
      "risk_level": "low",
      "approval_required": false
    },
    {
      "name": "restart_service",
      "description": "Restart a service to resolve operational issues",
      "risk_level": "medium",
      "approval_required": false
    },
    {
      "name": "escalate_to_human",
      "description": "Escalate an incident to human review for complex issues",
      "risk_level": "high",
      "approval_required": true
    }
  ]
  ```

### 3.2 Get Tools by Category
* **Endpoint:** `/tools/by-category`
* **Method:** `GET`
* **Purpose:** Retrieve tools organized by functional category.
* **Response Body (`200 OK`):**
  ```json
  {
    "Knowledge": [
      {
        "name": "search_knowledge_base",
        "description": "Search the knowledge base for relevant articles and procedures",
        "risk_level": "low",
        "approval_required": false
      }
    ],
    "Remediation": [
      {
        "name": "reset_vpn_token",
        "description": "Reset user VPN token to resolve authentication issues",
        "risk_level": "low",
        "approval_required": false
      }
    ]
  }
  ```

### 3.3 Execute Tool
* **Endpoint:** `/tools/execute`
* **Method:** `POST`
* **Purpose:** Execute a registered tool with validated inputs.
* **Request Body:**
  ```json
  {
    "name": "reset_vpn_token",
    "parameters": {
      "user_id": "usr_9482"
    }
  }
  ```
* **Response Body (`200 OK`):**
  ```json
  {
    "success": true,
    "tool": "reset_vpn_token",
    "status": "success",
    "message": "VPN token reset successfully for user 'usr_9482'",
    "data": {
      "user_id": "usr_9482",
      "token_reset": true,
      "new_token_hash": "TOKEN_HASH_usr_9482"
    },
    "error_code": null,
    "timestamp": "2026-10-01T11:30:00Z"
  }
  ```
* **Error Responses:**
  * `400 Bad Request`: Invalid tool name or invalid inputs
  * `403 Forbidden`: Tool requires human approval
  * `500 Internal Server Error`: Tool execution failed
