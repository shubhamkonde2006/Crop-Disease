from fastapi import APIRouter
from app.database import get_dashboard_statistics
from app.models.schemas import DashboardStats

router = APIRouter(prefix="/stats", tags=["Analytics & Dashboard"])

@router.get(
    "",
    response_model=DashboardStats,
    summary="Get aggregated statistics and distributions calculated from real scan records"
)
async def get_stats() -> DashboardStats:
    stats_data = get_dashboard_statistics()
    return DashboardStats(**stats_data)
