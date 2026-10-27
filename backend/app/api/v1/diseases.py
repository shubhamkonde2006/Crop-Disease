from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.services.knowledge_service import knowledge_service

router = APIRouter(prefix="", tags=["Disease Knowledge Base"])

class DiseaseInfoItem(BaseModel):
    raw_class_name: str
    display_name: str
    crop: str
    disease_name: str
    pathogen: Optional[str] = None
    is_healthy: bool
    severity: str
    common_symptoms: List[str]
    contributing_factors: List[str]
    prevention_practices: List[str]
    general_management: List[str]
    expert_guidance: str

@router.get(
    "/diseases",
    response_model=List[DiseaseInfoItem],
    summary="Searchable disease information catalog backed by credible agronomic sources"
)
async def list_diseases(
    query: Optional[str] = Query(None, description="Search keyword in disease name, crop, or symptoms"),
    crop: Optional[str] = Query(None, description="Filter by crop name")
) -> List[DiseaseInfoItem]:
    diseases = knowledge_service.search_diseases(query=query, crop=crop)
    return [DiseaseInfoItem(**d) for d in diseases]

@router.get(
    "/diseases/{raw_class_name}",
    response_model=DiseaseInfoItem,
    summary="Get detailed disease dossier and treatment guidelines"
)
async def get_disease_detail(raw_class_name: str) -> DiseaseInfoItem:
    guidance = knowledge_service.get_guidance(raw_class_name)
    if not guidance:
        raise HTTPException(status_code=404, detail="Disease profile not found.")
    return DiseaseInfoItem(
        raw_class_name=raw_class_name,
        display_name=f"{guidance['crop']} - {guidance['disease_name']}",
        **guidance
    )

@router.get(
    "/crops",
    response_model=List[str],
    summary="Get list of all 14 supported crops"
)
async def get_crops() -> List[str]:
    return knowledge_service.get_supported_crops()
