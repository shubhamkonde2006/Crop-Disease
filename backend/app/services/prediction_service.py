import json
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from PIL import Image

from app.config import settings
from app.database import insert_scan
from app.ml.model_service import model_service
from app.ml.preprocessor import validate_and_open_image, PreprocessingError
from app.services.knowledge_service import knowledge_service

class PredictionService:
    @staticmethod
    def save_image_and_thumbnail(image: Image.Image) -> tuple[str, Path, Path]:
        """
        Saves the uploaded image and a 256x256 thumbnail with unique UUID.
        Returns (filename, image_path, thumbnail_path).
        """
        file_id = str(uuid.uuid4())
        filename = f"{file_id}.jpg"

        image_path = settings.uploads_dir / filename
        thumb_path = settings.thumbnails_dir / f"thumb_{filename}"

        # Resize image for safe, storage-efficient archival (max 1280px width/height)
        archival_image = image.copy()
        archival_image.thumbnail((1280, 1280), Image.Resampling.LANCZOS)
        archival_image.save(image_path, "JPEG", quality=88, optimize=True)

        # Generate thumbnail
        thumb_image = image.copy()
        thumb_image.thumbnail((256, 256), Image.Resampling.LANCZOS)
        thumb_image.save(thumb_path, "JPEG", quality=85, optimize=True)

        return filename, image_path, thumb_path

    @classmethod
    def process_and_predict(
        cls,
        file_bytes: bytes,
        original_filename: str,
        content_type: Optional[str] = None,
        crop_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        End-to-end pipeline:
        1. Validate & open image.
        2. Run ML inference & OOD check.
        3. Retrieve disease knowledge.
        4. Save image & thumbnail.
        5. Persist record to database.
        6. Return complete structured prediction result.
        """
        # Step 1: Image validation and orientation correction
        image = validate_and_open_image(file_bytes, original_filename, content_type)

        # Step 2: Run PyTorch inference
        inference_out = model_service.run_inference(image, crop_hint=crop_hint)

        top_result = inference_out["top_result"]
        raw_class_name = top_result["raw_class_name"]

        # Step 3: Disease knowledge retrieval
        guidance = knowledge_service.get_guidance(raw_class_name)

        # Step 4: Storage
        filename, _, _ = cls.save_image_and_thumbnail(image)
        scan_id = Path(filename).stem
        created_at = datetime.utcnow().isoformat() + "Z"

        # Step 5: Database record preparation
        scan_record = {
            "id": scan_id,
            "filename": filename,
            "crop": top_result["crop"],
            "disease_name": top_result["disease_name"],
            "raw_class_name": raw_class_name,
            "display_name": top_result["display_name"],
            "confidence": inference_out["confidence"],
            "is_healthy": 1 if top_result["is_healthy"] else 0,
            "is_uncertain": 1 if inference_out["is_uncertain"] else 0,
            "uncertainty_score": inference_out["uncertainty_score"],
            "ood_warning": inference_out["quality_info"]["combined_warning"],
            "alternatives_json": json.dumps(inference_out["alternatives"]),
            "guidance_json": json.dumps(guidance),
            "processing_time_ms": inference_out["processing_time_ms"],
            "model_version": inference_out["model_version"],
            "created_at": created_at
        }

        insert_scan(scan_record)

        # Step 6: Return structured response
        return {
            "id": scan_id,
            "image_url": f"/uploads/{filename}",
            "thumbnail_url": f"/uploads/thumbnails/thumb_{filename}",
            "crop": top_result["crop"],
            "disease_name": top_result["disease_name"],
            "raw_class_name": raw_class_name,
            "display_name": top_result["display_name"],
            "confidence": inference_out["confidence"],
            "is_healthy": top_result["is_healthy"],
            "is_uncertain": inference_out["is_uncertain"],
            "uncertainty_score": inference_out["uncertainty_score"],
            "ood_warning": inference_out["quality_info"]["combined_warning"],
            "alternatives": inference_out["alternatives"],
            "guidance": guidance,
            "processing_time_ms": inference_out["processing_time_ms"],
            "model_version": inference_out["model_version"],
            "is_demo_mode": inference_out["is_demo_mode"],
            "created_at": created_at
        }
