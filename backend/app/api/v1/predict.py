import json
from pathlib import Path
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, File, Form, HTTPException, UploadFile, status
from pydantic import BaseModel

from app.config import settings
from app.ml.preprocessor import PreprocessingError
from app.models.schemas import PredictionResult, SampleLeaf
from app.services.prediction_service import PredictionService

router = APIRouter(prefix="", tags=["Inference & Prediction"])

class SamplePredictRequest(BaseModel):
    sample_id: str
    crop: Optional[str] = None

@router.post(
    "/predict",
    response_model=PredictionResult,
    summary="Run AI crop disease detection on uploaded leaf image",
    description="Validates image format and size, runs PyTorch MobileNetV3 inference, determines uncertainty, and retrieves agronomic management advice."
)
async def predict_crop_disease(
    file: UploadFile = File(..., description="Crop leaf image (JPEG, PNG, or WebP)"),
    crop: Optional[str] = Form(None, description="Optional crop hint to filter predictions")
) -> PredictionResult:
    # Basic extension validation
    filename = file.filename or "upload.jpg"
    suffix = Path(filename).suffix.lower()
    if suffix not in settings.allowed_extensions:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{suffix}'. Allowed formats: {', '.join(settings.allowed_extensions)}"
        )

    # Read bytes safely
    try:
        content = await file.read()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to read uploaded file: {str(e)}"
        )

    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The uploaded file is empty."
        )

    if len(content) > settings.max_upload_size_bytes:
        max_mb = settings.max_upload_size_bytes // (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Uploaded image exceeds maximum size limit of {max_mb} MB."
        )

    # Process and run inference pipeline
    try:
        result = PredictionService.process_and_predict(
            file_bytes=content,
            original_filename=filename,
            content_type=file.content_type,
            crop_hint=crop if crop and crop.strip() else None
        )
        return PredictionResult(**result)
    except PreprocessingError as pe:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(pe)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ML inference processing error: {str(e)}"
        )

@router.get(
    "/samples",
    response_model=List[SampleLeaf],
    summary="Get available sample leaf images for quick 1-click testing"
)
async def get_sample_leaves() -> List[SampleLeaf]:
    manifest_path = settings.sample_dir / "samples_manifest.json"
    if not manifest_path.exists():
        return []
    with open(manifest_path, "r", encoding="utf-8") as f:
        samples = json.load(f)
    return [
        SampleLeaf(
            id=s["id"],
            crop=s["crop"],
            expected_disease=s["expected_disease"],
            display_name=s["display_name"],
            description=f"Curated {s['crop']} leaf with {s['expected_disease']} symptoms",
            image_url=s["image_url"]
        )
        for s in samples
    ]

@router.post(
    "/predict/sample",
    response_model=PredictionResult,
    summary="Run AI detection on a pre-loaded sample leaf image"
)
async def predict_sample_leaf(request: SamplePredictRequest) -> PredictionResult:
    manifest_path = settings.sample_dir / "samples_manifest.json"
    if not manifest_path.exists():
        raise HTTPException(status_code=404, detail="Sample library is empty.")

    with open(manifest_path, "r", encoding="utf-8") as f:
        samples = json.load(f)

    target_sample = next((s for s in samples if s["id"] == request.sample_id), None)
    if not target_sample:
        raise HTTPException(status_code=404, detail=f"Sample '{request.sample_id}' not found.")

    sample_file_path = settings.sample_dir / target_sample["filename"]
    if not sample_file_path.exists():
        raise HTTPException(status_code=404, detail="Sample image file missing on server.")

    with open(sample_file_path, "rb") as f:
        file_bytes = f.read()

    try:
        result = PredictionService.process_and_predict(
            file_bytes=file_bytes,
            original_filename=target_sample["filename"],
            content_type="image/jpeg",
            crop_hint=request.crop or target_sample["crop"]
        )
        return PredictionResult(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference failed on sample: {str(e)}")
