"""
PlantVillage 38 Class Mapping and Definitions.
Standard benchmark dataset mapping 14 crops and 38 conditions (healthy + diseased).
"""

from typing import Dict, List, Optional, TypedDict

class ClassMetadata(TypedDict):
    id: int
    raw_class_name: str
    crop: str
    disease_name: str
    display_name: str
    is_healthy: bool

# Standard 38 PlantVillage Classes ordered by alphabetical convention
PLANTVILLAGE_CLASSES: List[ClassMetadata] = [
    {
        "id": 0,
        "raw_class_name": "Apple___Apple_scab",
        "crop": "Apple",
        "disease_name": "Apple Scab",
        "display_name": "Apple - Apple Scab",
        "is_healthy": False,
    },
    {
        "id": 1,
        "raw_class_name": "Apple___Black_rot",
        "crop": "Apple",
        "disease_name": "Black Rot",
        "display_name": "Apple - Black Rot",
        "is_healthy": False,
    },
    {
        "id": 2,
        "raw_class_name": "Apple___Cedar_apple_rust",
        "crop": "Apple",
        "disease_name": "Cedar Apple Rust",
        "display_name": "Apple - Cedar Apple Rust",
        "is_healthy": False,
    },
    {
        "id": 3,
        "raw_class_name": "Apple___healthy",
        "crop": "Apple",
        "disease_name": "Healthy",
        "display_name": "Apple - Healthy Leaf",
        "is_healthy": True,
    },
    {
        "id": 4,
        "raw_class_name": "Blueberry___healthy",
        "crop": "Blueberry",
        "disease_name": "Healthy",
        "display_name": "Blueberry - Healthy Leaf",
        "is_healthy": True,
    },
    {
        "id": 5,
        "raw_class_name": "Cherry_(including_sour)___Powdery_mildew",
        "crop": "Cherry",
        "disease_name": "Powdery Mildew",
        "display_name": "Cherry - Powdery Mildew",
        "is_healthy": False,
    },
    {
        "id": 6,
        "raw_class_name": "Cherry_(including_sour)___healthy",
        "crop": "Cherry",
        "disease_name": "Healthy",
        "display_name": "Cherry - Healthy Leaf",
        "is_healthy": True,
    },
    {
        "id": 7,
        "raw_class_name": "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
        "crop": "Corn",
        "disease_name": "Gray Leaf Spot (Cercospora)",
        "display_name": "Corn - Gray Leaf Spot",
        "is_healthy": False,
    },
    {
        "id": 8,
        "raw_class_name": "Corn_(maize)___Common_rust_",
        "crop": "Corn",
        "disease_name": "Common Rust",
        "display_name": "Corn - Common Rust",
        "is_healthy": False,
    },
    {
        "id": 9,
        "raw_class_name": "Corn_(maize)___Northern_Leaf_Blight",
        "crop": "Corn",
        "disease_name": "Northern Leaf Blight",
        "display_name": "Corn - Northern Leaf Blight",
        "is_healthy": False,
    },
    {
        "id": 10,
        "raw_class_name": "Corn_(maize)___healthy",
        "crop": "Corn",
        "disease_name": "Healthy",
        "display_name": "Corn - Healthy Leaf",
        "is_healthy": True,
    },
    {
        "id": 11,
        "raw_class_name": "Grape___Black_rot",
        "crop": "Grape",
        "disease_name": "Black Rot",
        "display_name": "Grape - Black Rot",
        "is_healthy": False,
    },
    {
        "id": 12,
        "raw_class_name": "Grape___Esca_(Black_Measles)",
        "crop": "Grape",
        "disease_name": "Black Measles (Esca)",
        "display_name": "Grape - Esca (Black Measles)",
        "is_healthy": False,
    },
    {
        "id": 13,
        "raw_class_name": "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
        "crop": "Grape",
        "disease_name": "Leaf Blight (Isariopsis)",
        "display_name": "Grape - Leaf Blight (Isariopsis)",
        "is_healthy": False,
    },
    {
        "id": 14,
        "raw_class_name": "Grape___healthy",
        "crop": "Grape",
        "disease_name": "Healthy",
        "display_name": "Grape - Healthy Leaf",
        "is_healthy": True,
    },
    {
        "id": 15,
        "raw_class_name": "Orange___Haunglongbing_(Citrus_greening)",
        "crop": "Orange",
        "disease_name": "Citrus Greening (Huanglongbing)",
        "display_name": "Orange - Citrus Greening",
        "is_healthy": False,
    },
    {
        "id": 16,
        "raw_class_name": "Peach___Bacterial_spot",
        "crop": "Peach",
        "disease_name": "Bacterial Spot",
        "display_name": "Peach - Bacterial Spot",
        "is_healthy": False,
    },
    {
        "id": 17,
        "raw_class_name": "Peach___healthy",
        "crop": "Peach",
        "disease_name": "Healthy",
        "display_name": "Peach - Healthy Leaf",
        "is_healthy": True,
    },
    {
        "id": 18,
        "raw_class_name": "Pepper,_bell___Bacterial_spot",
        "crop": "Bell Pepper",
        "disease_name": "Bacterial Spot",
        "display_name": "Bell Pepper - Bacterial Spot",
        "is_healthy": False,
    },
    {
        "id": 19,
        "raw_class_name": "Pepper,_bell___healthy",
        "crop": "Bell Pepper",
        "disease_name": "Healthy",
        "display_name": "Bell Pepper - Healthy Leaf",
        "is_healthy": True,
    },
    {
        "id": 20,
        "raw_class_name": "Potato___Early_blight",
        "crop": "Potato",
        "disease_name": "Early Blight",
        "display_name": "Potato - Early Blight",
        "is_healthy": False,
    },
    {
        "id": 21,
        "raw_class_name": "Potato___Late_blight",
        "crop": "Potato",
        "disease_name": "Late Blight",
        "display_name": "Potato - Late Blight",
        "is_healthy": False,
    },
    {
        "id": 22,
        "raw_class_name": "Potato___healthy",
        "crop": "Potato",
        "disease_name": "Healthy",
        "display_name": "Potato - Healthy Leaf",
        "is_healthy": True,
    },
    {
        "id": 23,
        "raw_class_name": "Raspberry___healthy",
        "crop": "Raspberry",
        "disease_name": "Healthy",
        "display_name": "Raspberry - Healthy Leaf",
        "is_healthy": True,
    },
    {
        "id": 24,
        "raw_class_name": "Soybean___healthy",
        "crop": "Soybean",
        "disease_name": "Healthy",
        "display_name": "Soybean - Healthy Leaf",
        "is_healthy": True,
    },
    {
        "id": 25,
        "raw_class_name": "Squash___Powdery_mildew",
        "crop": "Squash",
        "disease_name": "Powdery Mildew",
        "display_name": "Squash - Powdery Mildew",
        "is_healthy": False,
    },
    {
        "id": 26,
        "raw_class_name": "Strawberry___Leaf_scorch",
        "crop": "Strawberry",
        "disease_name": "Leaf Scorch",
        "display_name": "Strawberry - Leaf Scorch",
        "is_healthy": False,
    },
    {
        "id": 27,
        "raw_class_name": "Strawberry___healthy",
        "crop": "Strawberry",
        "disease_name": "Healthy",
        "display_name": "Strawberry - Healthy Leaf",
        "is_healthy": True,
    },
    {
        "id": 28,
        "raw_class_name": "Tomato___Bacterial_spot",
        "crop": "Tomato",
        "disease_name": "Bacterial Spot",
        "display_name": "Tomato - Bacterial Spot",
        "is_healthy": False,
    },
    {
        "id": 29,
        "raw_class_name": "Tomato___Early_blight",
        "crop": "Tomato",
        "disease_name": "Early Blight",
        "display_name": "Tomato - Early Blight",
        "is_healthy": False,
    },
    {
        "id": 30,
        "raw_class_name": "Tomato___Late_blight",
        "crop": "Tomato",
        "disease_name": "Late Blight",
        "display_name": "Tomato - Late Blight",
        "is_healthy": False,
    },
    {
        "id": 31,
        "raw_class_name": "Tomato___Leaf_Mold",
        "crop": "Tomato",
        "disease_name": "Leaf Mold",
        "display_name": "Tomato - Leaf Mold",
        "is_healthy": False,
    },
    {
        "id": 32,
        "raw_class_name": "Tomato___Septoria_leaf_spot",
        "crop": "Tomato",
        "disease_name": "Septoria Leaf Spot",
        "display_name": "Tomato - Septoria Leaf Spot",
        "is_healthy": False,
    },
    {
        "id": 33,
        "raw_class_name": "Tomato___Spider_mites Two-spotted_spider_mite",
        "crop": "Tomato",
        "disease_name": "Two-Spotted Spider Mites",
        "display_name": "Tomato - Two-Spotted Spider Mites",
        "is_healthy": False,
    },
    {
        "id": 34,
        "raw_class_name": "Tomato___Target_Spot",
        "crop": "Tomato",
        "disease_name": "Target Spot",
        "display_name": "Tomato - Target Spot",
        "is_healthy": False,
    },
    {
        "id": 35,
        "raw_class_name": "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
        "crop": "Tomato",
        "disease_name": "Yellow Leaf Curl Virus",
        "display_name": "Tomato - Yellow Leaf Curl Virus",
        "is_healthy": False,
    },
    {
        "id": 36,
        "raw_class_name": "Tomato___Tomato_mosaic_virus",
        "crop": "Tomato",
        "disease_name": "Tomato Mosaic Virus",
        "display_name": "Tomato - Mosaic Virus",
        "is_healthy": False,
    },
    {
        "id": 37,
        "raw_class_name": "Tomato___healthy",
        "crop": "Tomato",
        "disease_name": "Healthy",
        "display_name": "Tomato - Healthy Leaf",
        "is_healthy": True,
    },
]

ID_TO_METADATA: Dict[int, ClassMetadata] = {item["id"]: item for item in PLANTVILLAGE_CLASSES}
RAW_TO_METADATA: Dict[str, ClassMetadata] = {item["raw_class_name"]: item for item in PLANTVILLAGE_CLASSES}

SUPPORTED_CROPS: List[str] = sorted(list({item["crop"] for item in PLANTVILLAGE_CLASSES}))

def get_class_metadata(class_id: int) -> Optional[ClassMetadata]:
    return ID_TO_METADATA.get(class_id)

def get_crop_classes(crop_name: str) -> List[ClassMetadata]:
    return [c for c in PLANTVILLAGE_CLASSES if c["crop"].lower() == crop_name.lower()]
