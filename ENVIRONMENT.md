# ENVIRONMENT — Environment Configuration & Variables Guide

## ResolveAI — AI IT Service Desk Autonomous Resolution Agent

**Version:** 1.0  
**Security Notice:** NEVER commit real API keys, secrets, or production credentials to source control. Use local `.env` files matching the template below.

---

## 1. Environment Variable Reference

| Variable Name | Type | Default Value | Description |
| :--- | :--- | :--- | :--- |
| `ENVIRONMENT` | String | `development` | Runtime environment (`development`, `test`, `production`). |
| `BACKEND_PORT` | Integer | `8000` | Port for the FastAPI server. |
| `FRONTEND_PORT` | Integer | `5173` | Port for the Vite frontend server. |
| `DATABASE_URL` | String | `sqlite:///./resolveai.db` | Connection URI for the SQLite database. |
| `CORS_ORIGINS` | String (CSV) | `http://localhost:5173,http://127.0.0.1:5173` | Allowed CORS origins for frontend-backend communication. |
| `ANTHROPIC_API_KEY` | Secret String | `your-anthropic-api-key-here` | Anthropic Claude API Key for agent LLM reasoning. |
| `OPENAI_API_KEY` | Secret String | `your-openai-api-key-here` | (Optional) OpenAI API Key for embeddings / fallback LLM. |
| `LOG_LEVEL` | String | `INFO` | Logging verbosity (`DEBUG`, `INFO`, `WARNING`, `ERROR`). |
| `ENABLE_MOCK_LLM` | Boolean | `false` | When `true`, runs deterministic mock LLM agent pipelines without calling external APIs (useful for offline testing/demos). |

---

## 2. Configuration Templates

### 2.1 Backend `.env.example`
Create a `.env` file in `backend/` based on the following template:

```env
# ==============================================================================
# ResolveAI Backend Environment Configuration Template
# ==============================================================================

# Application Environment
ENVIRONMENT=development
LOG_LEVEL=INFO
ENABLE_MOCK_LLM=false

# Server Ports & Hosts
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173

# Database Connection
DATABASE_URL=sqlite:///./resolveai.db

# AI & LLM Provider Credentials (NEVER COMMIT REAL KEYS)
ANTHROPIC_API_KEY=your-anthropic-api-key-here
OPENAI_API_KEY=your-openai-api-key-here
```

### 2.2 Frontend `.env.example`
Create a `.env` file in `frontend/` if overriding the default API proxy:

```env
# ==============================================================================
# ResolveAI Frontend Environment Configuration Template
# ==============================================================================

VITE_API_BASE_URL=http://localhost:8000/api
VITE_ENABLE_MOCK_MODE=false
```

---

## 3. Setup Instructions

1. Copy `.env.example` to `.env`:
   ```bash
   cp backend/.env.example backend/.env
   ```
2. Insert your valid API key in `ANTHROPIC_API_KEY`.
3. If running in an offline or rate-limited environment, set `ENABLE_MOCK_LLM=true` to utilize the pre-compiled deterministic agent responses for the 3 demo scenarios.
