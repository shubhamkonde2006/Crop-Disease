from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class AlternativePrediction(BaseModel):
    class_id: int
    raw_class_name: str
    crop: str
    disease_name: str
    display_name: str
    confidence: float
    is_healthy: bool

class DiseaseGuidance(BaseModel):
    crop: str
    disease_name: str
    pathogen: Optional[str] = None
    is_healthy: bool
    severity: str = "low"
    common_symptoms: List[str] = []
    contributing_factors: List[str] = []
    prevention_practices: List[str] = []
    general_management: List[str] = []
    expert_guidance: str

class PredictionResult(BaseModel):
    id: str
    image_url: str
    thumbnail_url: str
    crop: str
    disease_name: str
    raw_class_name: str
    display_name: str
    confidence: float = Field(..., ge=0.0, le=1.0)
    is_healthy: bool
    is_uncertain: bool = False
    uncertainty_score: float = 0.0
    ood_warning: Optional[str] = None
    alternatives: List[AlternativePrediction] = []
    guidance: DiseaseGuidance
    processing_time_ms: float
    model_version: str
    created_at: str

class ScanHistoryItem(BaseModel):
    id: str
    crop: str
    disease_name: str
    display_name: str
    confidence: float
    is_healthy: bool
    is_uncertain: bool
    thumbnail_url: str
    image_url: str
    created_at: str

class ScanHistoryDetail(PredictionResult):
    pass

class CropSummary(BaseModel):
    crop: str
    total_scans: int
    healthy_scans: int
    diseased_scans: int

class DiseaseCount(BaseModel):
    disease_name: str
    crop: str
    count: int

class DashboardStats(BaseModel):
    total_scans: int
    healthy_count: int
    diseased_count: int
    uncertain_count: int
    healthy_percentage: float
    crop_distribution: List[CropSummary]
    disease_distribution: List[DiseaseCount]
    recent_activity: List[ScanHistoryItem]

class ModelInfoResponse(BaseModel):
    architecture: str
    device: str
    num_classes: int
    confidence_threshold: float
    uncertainty_threshold: float
    supported_crops: List[str]
    total_classes: int
    status: str
    is_demo_mode: bool
    weights_path: str
    description: str

class SampleLeaf(BaseModel):
    id: str
    crop: str
    expected_disease: str
    display_name: str
    description: str
    image_url: str
