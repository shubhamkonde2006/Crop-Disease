import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from app.config import settings
from app.ml.class_mapping import SUPPORTED_CROPS, RAW_TO_METADATA

class KnowledgeService:
    _instance: Optional["KnowledgeService"] = None

    def __init__(self):
        self.kb_data: Dict[str, Dict[str, Any]] = {}
        self.load_kb()

    @classmethod
    def get_instance(cls) -> "KnowledgeService":
        if cls._instance is None:
            cls._instance = KnowledgeService()
        return cls._instance

    def load_kb(self) -> None:
        kb_path = settings.disease_kb_path
        if kb_path.exists():
            with open(kb_path, "r", encoding="utf-8") as f:
                self.kb_data = json.load(f)
            print(f"[KnowledgeService] Loaded {len(self.kb_data)} disease knowledge items.")
        else:
            print(f"[KnowledgeService] Warning: Knowledge base not found at {kb_path}")

    def get_guidance(self, raw_class_name: str) -> Dict[str, Any]:
        """Returns structured guidance for a predicted class."""
        if raw_class_name in self.kb_data:
            return self.kb_data[raw_class_name]

        # Fallback if specific key is missing
        meta = RAW_TO_METADATA.get(raw_class_name, {
            "crop": "General Crop",
            "disease_name": "Unspecified Condition",
            "is_healthy": False
        })
        return {
            "crop": meta["crop"],
            "disease_name": meta["disease_name"],
            "pathogen": "Unknown",
            "is_healthy": meta["is_healthy"],
            "severity": "medium",
            "common_symptoms": ["Leaf discoloration or spotting observed."],
            "contributing_factors": ["Favorable humidity or nutrient imbalance."],
            "prevention_practices": ["Maintain clean cultivation hygiene and inspect regularly."],
            "general_management": ["Consult a local agricultural extension specialist."],
            "expert_guidance": "Please reach out to your local agronomy extension office for diagnostic confirmation."
        }

    def search_diseases(
        self,
        query: Optional[str] = None,
        crop: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        results = []
        for raw_name, info in self.kb_data.items():
            meta = RAW_TO_METADATA.get(raw_name)
            display_name = meta["display_name"] if meta else f"{info['crop']} - {info['disease_name']}"

            # Filter by crop
            if crop and info["crop"].lower() != crop.lower():
                continue

            # Search query matching
            if query:
                q = query.lower()
                matches = (
                    q in info["crop"].lower()
                    or q in info["disease_name"].lower()
                    or q in info.get("pathogen", "").lower()
                    or any(q in s.lower() for s in info.get("common_symptoms", []))
                )
                if not matches:
                    continue

            item = dict(info)
            item["raw_class_name"] = raw_name
            item["display_name"] = display_name
            results.append(item)

        results.sort(key=lambda x: (x["crop"], x["disease_name"]))
        return results

    def get_supported_crops(self) -> List[str]:
        return SUPPORTED_CROPS


knowledge_service = KnowledgeService.get_instance()
