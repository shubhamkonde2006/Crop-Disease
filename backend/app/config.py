import os
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "app" / "data"
UPLOADS_DIR = BASE_DIR / "uploads"
THUMBNAILS_DIR = UPLOADS_DIR / "thumbnails"
SAMPLE_DIR = DATA_DIR / "sample_images"
DB_PATH = BASE_DIR / "crop_disease.db"
MODEL_WEIGHTS_PATH = BASE_DIR / "models" / "crop_mobilenet_v3.pth"

# Ensure directories exist
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)
SAMPLE_DIR.mkdir(parents=True, exist_ok=True)
MODEL_WEIGHTS_PATH.parent.mkdir(parents=True, exist_ok=True)


class Settings(BaseModel):
    app_name: str = "AgriShield - AI Crop Disease Detection"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Storage limits
    max_upload_size_bytes: int = 10 * 1024 * 1024  # 10 MB
    max_image_dimension: int = 4096  # pixels
    allowed_mime_types: set[str] = {
        "image/jpeg",
        "image/png",
        "image/webp"
    }
    allowed_extensions: set[str] = {".jpg", ".jpeg", ".png", ".webp"}
    
    # Model configuration
    model_architecture: str = "mobilenet_v3_small"
    num_classes: int = 38
    input_size: int = 224
    confidence_threshold: float = 0.50
    uncertainty_entropy_threshold: float = 2.4
    
    # Paths
    base_dir: Path = BASE_DIR
    uploads_dir: Path = UPLOADS_DIR
    thumbnails_dir: Path = THUMBNAILS_DIR
    sample_dir: Path = SAMPLE_DIR
    db_path: Path = DB_PATH
    model_weights_path: Path = MODEL_WEIGHTS_PATH
    disease_kb_path: Path = DATA_DIR / "disease_kb.json"


settings = Settings()
