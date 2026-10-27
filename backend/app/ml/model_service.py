import math
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from PIL import Image
import torch

from app.config import settings
from app.ml.class_mapping import (
    PLANTVILLAGE_CLASSES,
    ID_TO_METADATA,
    SUPPORTED_CROPS,
    ClassMetadata,
    get_class_metadata
)
from app.ml.preprocessor import (
    check_image_quality_and_ood,
    preprocess_for_inference
)
from app.ml.weights_manager import build_model, ensure_model_weights

class ModelService:
    _instance: Optional["ModelService"] = None

    def __init__(self):
        self.device = torch.device("cpu")
        self.model: Optional[torch.nn.Module] = None
        self.is_loaded: bool = False
        self.is_demo_mode: bool = False
        self.weights_version: str = "unknown"

    @classmethod
    def get_instance(cls) -> "ModelService":
        if cls._instance is None:
            cls._instance = ModelService()
        return cls._instance

    def load_model(self) -> None:
        """Loads the PyTorch MobileNetV3 model once into memory."""
        print(f"[ModelService] Initializing {settings.model_architecture} on {self.device}...")
        start_time = time.perf_counter()

        # Ensure weights file exists
        ensure_model_weights()

        model = build_model(num_classes=settings.num_classes)
        weights_path = settings.model_weights_path

        try:
            checkpoint = torch.load(str(weights_path), map_location=self.device)
            if isinstance(checkpoint, dict) and "state_dict" in checkpoint:
                model.load_state_dict(checkpoint["state_dict"])
                self.weights_version = checkpoint.get("version", "1.0.0")
            else:
                model.load_state_dict(checkpoint)
                self.weights_version = "1.0.0"
            self.is_demo_mode = "calibrated" in self.weights_version
            print(f"[ModelService] Loaded weights from {weights_path} (version: {self.weights_version})")
        except Exception as e:
            print(f"[ModelService] Warning: Failed to load state_dict ({e}). Running in fallback mode.")
            self.is_demo_mode = True
            self.weights_version = "fallback-unweighted"

        model.to(self.device)
        model.eval()
        self.model = model
        self.is_loaded = True
        elapsed = (time.perf_counter() - start_time) * 1000.0
        print(f"[ModelService] Model ready in {elapsed:.1f}ms (demo_mode={self.is_demo_mode})")

    def run_inference(
        self,
        image: Image.Image,
        crop_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Executes genuine PyTorch inference pipeline on a PIL Image.
        Returns full diagnostic predictions, uncertainty metrics, and alternative hypotheses.
        """
        if not self.is_loaded or self.model is None:
            raise RuntimeError("Model is not loaded. Call load_model() first.")

        start_time = time.perf_counter()

        # 1. Quality and Out-of-Distribution checks
        quality_info = check_image_quality_and_ood(image)

        # 2. Preprocess into tensor [1, 3, 224, 224]
        tensor = preprocess_for_inference(image).to(self.device)

        # 3. Model forward pass
        with torch.no_grad():
            logits = self.model(tensor)  # Shape: [1, 38]

        # 4. Softmax probability calculation
        temperature = 1.0
        scaled_logits = logits / temperature
        probabilities = torch.softmax(scaled_logits, dim=1)[0]  # Shape: [38]

        # 5. Shannon entropy calculation: H(p) = -sum(p * log(p))
        entropy = float(-torch.sum(probabilities * torch.log(probabilities + 1e-12)).item())

        # 6. Apply crop filtering if user selected a crop
        candidate_indices = list(range(settings.num_classes))
        if crop_hint:
            filtered_indices = [
                i for i, c in enumerate(PLANTVILLAGE_CLASSES)
                if c["crop"].lower() == crop_hint.lower()
            ]
            if filtered_indices:
                candidate_indices = filtered_indices

        # 7. Extract Top-5 predictions
        prob_list = probabilities.tolist()
        indexed_probs = [(i, prob_list[i]) for i in candidate_indices]
        indexed_probs.sort(key=lambda x: x[1], reverse=True)

        top_k = min(5, len(indexed_probs))
        top_predictions: List[Dict[str, Any]] = []

        for i in range(top_k):
            class_id, conf = indexed_probs[i]
            meta = ID_TO_METADATA[class_id]
            top_predictions.append({
                "class_id": class_id,
                "raw_class_name": meta["raw_class_name"],
                "crop": meta["crop"],
                "disease_name": meta["disease_name"],
                "display_name": meta["display_name"],
                "confidence": round(float(conf), 4),
                "is_healthy": meta["is_healthy"]
            })

        top_result = top_predictions[0]
        top_confidence = top_result["confidence"]

        # 8. Calibrated uncertainty decision
        is_uncertain = (
            top_confidence < settings.confidence_threshold
            or entropy > settings.uncertainty_entropy_threshold
            or quality_info["is_ood"]
            or quality_info["is_blurry"]
        )

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return {
            "top_result": top_result,
            "alternatives": top_predictions[1:],
            "confidence": top_confidence,
            "entropy": round(entropy, 3),
            "is_uncertain": is_uncertain,
            "uncertainty_score": round(min(1.0, entropy / math.log(settings.num_classes)), 3),
            "quality_info": quality_info,
            "processing_time_ms": round(elapsed_ms, 2),
            "model_version": f"{settings.model_architecture} ({self.weights_version})",
            "is_demo_mode": self.is_demo_mode
        }


# Global singleton access
model_service = ModelService.get_instance()
