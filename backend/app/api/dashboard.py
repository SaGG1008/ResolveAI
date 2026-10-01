from fastapi import APIRouter
from ..models.schemas import DashboardMetrics
from ..core.db import db

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/metrics", response_model=DashboardMetrics)
async def get_dashboard_metrics():
    """Retrieve aggregate KPI metrics for dashboard."""
    return db.get_dashboard_metrics()
