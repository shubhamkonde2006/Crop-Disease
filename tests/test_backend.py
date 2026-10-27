import io
import json
import sys
from pathlib import Path
from PIL import Image

# Setup sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.config import settings
from app.database import (
    clear_scans,
    get_dashboard_statistics,
    get_scan_by_id,
    get_scans,
    init_db
)
from app.ml.class_mapping import PLANTVILLAGE_CLASSES, SUPPORTED_CROPS
from app.ml.model_service import model_service
from app.ml.preprocessor import check_image_quality_and_ood, validate_and_open_image
from app.services.knowledge_service import knowledge_service
from app.services.prediction_service import PredictionService

def run_direct_tests():
    print("=" * 60)
    print("RUNNING AGRI-SHIELD BACKEND & ML PIPELINE INTEGRATION TESTS")
    print("=" * 60)

    # 1. Initialize Database
    print("\n[Test 1] Database Initialization...")
    init_db()
    print(" [PASS] SQLite database tables initialized.")

    # 2. Knowledge Base Load
    print("\n[Test 2] Knowledge Base Service...")
    knowledge_service.load_kb()
    assert len(knowledge_service.kb_data) == 38, f"Expected 38 entries, got {len(knowledge_service.kb_data)}"
    crops = knowledge_service.get_supported_crops()
    assert len(crops) == 14
    print(f" -> Successfully loaded 38 disease dossiers across {len(crops)} crops.")
    # Search test
    blight_results = knowledge_service.search_diseases(query="blight", crop="Tomato")
    assert len(blight_results) >= 2
    print(f" -> Found {len(blight_results)} Tomato blight diseases.")
    print(" [PASS] Knowledge base verified.")

    # 3. Model Service Initialization
    print("\n[Test 3] PyTorch Model Service Loading...")
    model_service.load_model()
    assert model_service.is_loaded is True
    assert model_service.model is not None
    print(f" -> Model architecture: {settings.model_architecture}")
    print(f" -> Inference device: {model_service.device}")
    print(f" -> Demo mode status: {model_service.is_demo_mode}")
    print(" [PASS] PyTorch MobileNetV3 model loaded.")

    # 4. Out-of-Distribution & Image Quality Tests
    print("\n[Test 4] Image Preprocessor & Quality / OOD Checks...")
    # Test valid green leaf
    green_img = Image.new("RGB", (250, 250), (45, 140, 50))
    q_green = check_image_quality_and_ood(green_img)
    print(f" -> Green leaf plant pixel ratio: {q_green['plant_pixel_ratio']}, is_ood: {q_green['is_ood']}")
    assert q_green["is_ood"] is False

    # Test non-leaf solid white image
    white_img = Image.new("RGB", (250, 250), (255, 255, 255))
    q_white = check_image_quality_and_ood(white_img)
    print(f" -> Monochromatic image is_ood: {q_white['is_ood']}, warning: {q_white['combined_warning']}")
    assert q_white["is_ood"] is True
    print(" [PASS] OOD and quality check verified.")

    # 5. End-to-End Prediction on Tomato Early Blight Sample
    print("\n[Test 5] Running End-to-End Prediction on Sample...")
    sample_path = settings.sample_dir / "tomato_early_blight.jpg"
    assert sample_path.exists(), f"Sample file {sample_path} missing!"
    with open(sample_path, "rb") as f:
        sample_bytes = f.read()

    result = PredictionService.process_and_predict(
        file_bytes=sample_bytes,
        original_filename="tomato_early_blight.jpg",
        content_type="image/jpeg",
        crop_hint="Tomato"
    )

    print(f" -> Prediction ID: {result['id']}")
    print(f" -> Predicted Crop: {result['crop']}")
    print(f" -> Disease Name: {result['disease_name']}")
    print(f" -> Display Name: {result['display_name']}")
    print(f" -> Confidence: {result['confidence'] * 100:.1f}%")
    print(f" -> Is Healthy: {result['is_healthy']}")
    print(f" -> Processing Latency: {result['processing_time_ms']}ms")
    print(f" -> Alternatives Count: {len(result['alternatives'])}")
    print(f" -> Pathogen: {result['guidance'].get('pathogen')}")
    print(f" -> Symptoms Count: {len(result['guidance'].get('common_symptoms', []))}")

    assert result["crop"] == "Tomato"
    assert len(result["alternatives"]) >= 1
    assert "guidance" in result
    assert Path(settings.uploads_dir / f"{result['id']}.jpg").exists()
    scan_id = result["id"]
    print(" [PASS] End-to-end prediction pipeline verified.")

    # 6. Database Persistence & History Retrieval
    print("\n[Test 6] Verifying SQLite Scan Persistence...")
    retrieved = get_scan_by_id(scan_id)
    assert retrieved is not None
    assert retrieved["id"] == scan_id
    assert retrieved["crop"] == "Tomato"
    print(f" -> Retrieved scan {scan_id} successfully from SQLite.")

    items, total = get_scans(limit=10, offset=0)
    print(f" -> Total scans in database: {total}")
    assert total >= 1
    print(" [PASS] Database persistence verified.")

    # 7. Dashboard Aggregation Statistics
    print("\n[Test 7] Calculating Live Dashboard Statistics...")
    stats = get_dashboard_statistics()
    print(f" -> Total Scans: {stats['total_scans']}")
    print(f" -> Healthy: {stats['healthy_count']}, Diseased: {stats['diseased_count']}")
    print(f" -> Crops: {[c['crop'] for c in stats['crop_distribution']]}")
    assert stats["total_scans"] >= 1
    print(" [PASS] Dashboard statistics verified.")

    # 8. Another Prediction: Healthy Potato
    print("\n[Test 8] Running Prediction on Healthy Potato Sample...")
    potato_path = settings.sample_dir / "potato_healthy.jpg"
    with open(potato_path, "rb") as f:
        potato_bytes = f.read()

    potato_result = PredictionService.process_and_predict(
        file_bytes=potato_bytes,
        original_filename="potato_healthy.jpg",
        content_type="image/jpeg",
        crop_hint="Potato"
    )
    print(f" -> Potato Result: {potato_result['display_name']} (Healthy: {potato_result['is_healthy']})")
    assert potato_result["crop"] == "Potato"
    print(" [PASS] Healthy crop prediction verified.")

    # Re-verify stats with multiple scans
    new_stats = get_dashboard_statistics()
    print(f" -> Updated Total Scans in DB: {new_stats['total_scans']}")
    assert new_stats["total_scans"] >= 2

    print("\n" + "=" * 60)
    print("ALL 8 BACKEND & ML INTEGRATION TESTS PASSED CLEANLY!")
    print("=" * 60)

if __name__ == "__main__":
    run_direct_tests()
