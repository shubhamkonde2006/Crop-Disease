import io
from pathlib import Path
from typing import Dict, Optional, Tuple, Any

import numpy as np
from PIL import Image, ImageOps
import torch
import torchvision.transforms as T

from app.config import settings

# ImageNet normalization parameters standard for PyTorch vision models
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

# Preprocessing transform
INFERENCE_TRANSFORMS = T.Compose([
    T.Resize((settings.input_size, settings.input_size), interpolation=T.InterpolationMode.BILINEAR),
    T.ToTensor(),
    T.Normalize(mean=IMAGENET_MEAN, std=IMAGENET_STD)
])

class PreprocessingError(Exception):
    """Custom exception for image validation and preprocessing failures."""
    pass

def validate_and_open_image(
    file_bytes: bytes,
    filename: str,
    content_type: Optional[str] = None
) -> Image.Image:
    """
    Validates uploaded file size, extension, MIME type, and Pillow decoding.
    Applies EXIF orientation normalization and converts to RGB.
    """
    # 1. File size check
    size = len(file_bytes)
    if size == 0:
        raise PreprocessingError("The uploaded file is empty.")
    if size > settings.max_upload_size_bytes:
        max_mb = settings.max_upload_size_bytes // (1024 * 1024)
        raise PreprocessingError(f"File size exceeds maximum allowed limit of {max_mb} MB.")

    # 2. Extension check
    suffix = Path(filename).suffix.lower()
    if suffix not in settings.allowed_extensions:
        raise PreprocessingError(
            f"Unsupported file extension '{suffix}'. Allowed: {', '.join(settings.allowed_extensions)}"
        )

    # 3. Pillow decode check
    try:
        img = Image.open(io.BytesIO(file_bytes))
        img.verify()  # verify integrity
    except Exception as e:
        raise PreprocessingError(f"Corrupted or invalid image file: {str(e)}")

    # Re-open after verify() (Pillow requirement)
    img = Image.open(io.BytesIO(file_bytes))

    # 4. Dimension checks
    width, height = img.size
    if width < 32 or height < 32:
        raise PreprocessingError(f"Image dimensions ({width}x{height}) are too small for accurate detection.")
    if width > settings.max_image_dimension or height > settings.max_image_dimension:
        raise PreprocessingError(
            f"Image dimensions ({width}x{height}) exceed maximum allowed dimension of {settings.max_image_dimension}px."
        )

    # 5. Fix EXIF orientation (e.g. mobile camera pictures)
    try:
        img = ImageOps.exif_transpose(img)
    except Exception:
        pass

    # 6. Ensure RGB format
    if img.mode != "RGB":
        img = img.convert("RGB")

    return img

def check_image_quality_and_ood(image: Image.Image) -> Dict[str, Any]:
    """
    Analyzes image characteristics:
    - Blur / sharpness check
    - Plant/leaf tissue chromaticity (Excess Green / Foliar spectrum check)
    - Returns warning if low quality or unlikely to be a plant leaf.
    """
    np_img = np.array(image)
    h, w, _ = np_img.shape

    # 1. Check for blur via Laplacian variance
    # Grayscale conversion using ITU-R BT.601
    gray = (0.2989 * np_img[:, :, 0] + 0.5870 * np_img[:, :, 1] + 0.1140 * np_img[:, :, 2]).astype(np.float32)
    # Simple 3x3 Laplacian kernel discrete approximation
    lap = (
        -4 * gray[1:-1, 1:-1]
        + gray[:-2, 1:-1]
        + gray[2:, 1:-1]
        + gray[1:-1, :-2]
        + gray[1:-1, 2:]
    )
    blur_score = float(np.var(lap))
    is_blurry = blur_score < 30.0

    # 2. Plant / Leaf tissue chromaticity check (OOD check)
    # Compute Excess Green Index: 2G - R - B
    r = np_img[:, :, 0].astype(np.float32)
    g = np_img[:, :, 1].astype(np.float32)
    b = np_img[:, :, 2].astype(np.float32)
    
    exg = 2.0 * g - r - b
    # Foliar / vegetal pixels typically have positive ExG or characteristic golden/brown necrotic tones
    plant_pixel_ratio = float(np.mean((exg > 0) | ((g > 40) & (r > 40) & (b < 120))))
    
    # Color variance check (detect solid blocks, placeholder icons, synthetic blanks)
    rgb_std = float(np.std(np_img))
    is_monochrome = rgb_std < 12.0

    warnings = []
    is_ood = False

    if is_monochrome:
        is_ood = True
        warnings.append("Image appears to be a blank or monochromatic background. Please upload a clear photo of a crop leaf.")
    elif plant_pixel_ratio < 0.12:
        is_ood = True
        warnings.append("The uploaded image contains very little plant/leaf foliage. The result may be unreliable.")

    if is_blurry:
        warnings.append("The image appears blurry or out of focus. For highest accuracy, capture leaf veins sharply in bright daylight.")

    return {
        "is_blurry": is_blurry,
        "blur_score": round(blur_score, 2),
        "plant_pixel_ratio": round(plant_pixel_ratio, 3),
        "is_ood": is_ood,
        "warnings": warnings,
        "combined_warning": " ".join(warnings) if warnings else None
    }

def preprocess_for_inference(image: Image.Image) -> torch.Tensor:
    """
    Transforms PIL image into normalized PyTorch tensor with shape [1, 3, 224, 224].
    """
    tensor = INFERENCE_TRANSFORMS(image)
    return tensor.unsqueeze(0)  # Shape: (1, 3, 224, 224)
