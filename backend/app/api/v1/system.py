from datetime import datetime
from fastapi import APIRouter
from app.config import settings
from app.ml.class_mapping import SUPPORTED_CROPS, PLANTVILLAGE_CLASSES
from app.ml.model_service import model_service
from app.models.schemas import ModelInfoResponse

router = APIRouter(prefix="", tags=["System & Diagnostics"])

@router.get("/health", summary="Health check endpoint")
async def health_check():
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
        "model_loaded": model_service.is_loaded,
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }

@router.get(
    "/model-info",
    response_model=ModelInfoResponse,
    summary="Get ML model metadata, architecture details, and uncertainty thresholds"
)
async def get_model_info() -> ModelInfoResponse:
    return ModelInfoResponse(
        architecture=settings.model_architecture,
        device=str(model_service.device),
        num_classes=settings.num_classes,
        confidence_threshold=settings.confidence_threshold,
        uncertainty_threshold=settings.uncertainty_entropy_threshold,
        supported_crops=SUPPORTED_CROPS,
        total_classes=len(PLANTVILLAGE_CLASSES),
        status="active" if model_service.is_loaded else "uninitialized",
        is_demo_mode=model_service.is_demo_mode,
        weights_path=str(settings.model_weights_path),
        description=(
            "PyTorch MobileNetV3-Small classifier fine-tuned on PlantVillage benchmark dataset. "
            "Includes Shannon entropy uncertainty checks, OOD non-leaf detection, and blur analysis."
        )
    )
