import json
from pathlib import Path
from typing import Dict, Any
from fastapi import APIRouter
from ..tools.registry import tool_registry

router = APIRouter(prefix="/system", tags=["system"])
DATA_DIR = Path(__file__).resolve().parent.parent / "data"

@router.get("/status")
async def get_system_status() -> Dict[str, Any]:
    """Return backend status, available tools, and service health."""
    status_path = DATA_DIR / "system_status.json"
    services = []
    if status_path.exists():
        with open(status_path, "r", encoding="utf-8") as f:
            services = json.load(f).get("services", [])

    return {
        "status": "HEALTHY",
        "timestamp": "2026-10-01T15:30:00Z",
        "registered_tools": tool_registry.list_tools(),
        "services": services
    }
