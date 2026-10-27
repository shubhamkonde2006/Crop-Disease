from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query, status
from pydantic import BaseModel

from app.database import (
    clear_scans,
    delete_scan_by_id,
    get_scan_by_id,
    get_scans
)
from app.models.schemas import PredictionResult, ScanHistoryItem

router = APIRouter(prefix="/history", tags=["Prediction History"])

class HistoryListResponse(BaseModel):
    items: List[ScanHistoryItem]
    total: int
    limit: int
    offset: int

class DeleteResponse(BaseModel):
    success: bool
    message: str

@router.get(
    "",
    response_model=HistoryListResponse,
    summary="Get paginated prediction scan history with optional filters"
)
async def list_history(
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    crop: Optional[str] = Query(None, description="Filter by crop name"),
    is_healthy: Optional[bool] = Query(None, description="Filter by healthy (true) or diseased (false)"),
    search: Optional[str] = Query(None, description="Search term for crop, disease, or symptom")
) -> HistoryListResponse:
    items, total = get_scans(
        limit=limit,
        offset=offset,
        crop=crop,
        is_healthy=is_healthy,
        search=search
    )
    return HistoryListResponse(
        items=[ScanHistoryItem(**i) for i in items],
        total=total,
        limit=limit,
        offset=offset
    )

@router.get(
    "/{scan_id}",
    response_model=PredictionResult,
    summary="Get full prediction details and guidance for a past scan"
)
async def get_history_detail(scan_id: str) -> PredictionResult:
    scan = get_scan_by_id(scan_id)
    if not scan:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan record with ID '{scan_id}' not found."
        )
    return PredictionResult(**scan)

@router.delete(
    "/{scan_id}",
    response_model=DeleteResponse,
    summary="Delete a single scan record and its associated images"
)
async def delete_history_item(scan_id: str) -> DeleteResponse:
    deleted = delete_scan_by_id(scan_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan with ID '{scan_id}' does not exist."
        )
    return DeleteResponse(success=True, message=f"Scan '{scan_id}' deleted successfully.")

@router.delete(
    "",
    response_model=DeleteResponse,
    summary="Clear all scan history"
)
async def clear_all_history() -> DeleteResponse:
    count = clear_scans()
    return DeleteResponse(
        success=True,
        message=f"Cleared {count} scan records from history."
    )
