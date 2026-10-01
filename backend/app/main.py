import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core import env_loader # auto-loads .env and .env.local
from .api.incidents import router as incidents_router
from .api.dashboard import router as dashboard_router
from .api.system import router as system_router
from .api.tools import router as tools_router
from .core.db import db
from .tools import handlers # ensures tools are registered

app = FastAPI(
    title="ResolveAI API",
    description="Agentic AI IT Service Desk Autonomous Resolution Engine",
    version="1.0.0"
)

# Configure CORS
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount routers under /api
app.include_router(incidents_router, prefix="/api")
app.include_router(dashboard_router, prefix="/api")
app.include_router(system_router, prefix="/api")
app.include_router(tools_router, prefix="/api")

@app.get("/")
async def root():
    return {
        "name": "ResolveAI Backend API",
        "version": "1.0.0",
        "status": "OPERATIONAL",
        "docs_url": "/docs"
    }

@app.get("/health")
async def health():
    return {"status": "HEALTHY", "service": "ResolveAI"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
