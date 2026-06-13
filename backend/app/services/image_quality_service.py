from dataclasses import dataclass
from io import BytesIO

import cv2
import numpy as np
from PIL import Image


MIN_BLUR_SCORE = 80.0
MIN_BRIGHTNESS = 45.0
MAX_BRIGHTNESS = 230.0
MIN_EDGE_DENSITY = 0.01


@dataclass
class ImageQualityResult:
    quality_status: str
    blur_score: float
    brightness_score: float
    edge_density: float
    vehicle_visibility_status: str
    warnings: list[str]


def analyze_image_quality(file_bytes: bytes) -> ImageQualityResult:
    image = Image.open(BytesIO(file_bytes)).convert("RGB")
    image_array = np.array(image)

    gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)

    blur_score = float(cv2.Laplacian(gray, cv2.CV_64F).var())
    brightness_score = float(np.mean(gray))

    edges = cv2.Canny(gray, threshold1=100, threshold2=200)
    edge_density = float(np.count_nonzero(edges) / edges.size)

    warnings = []

    if blur_score < MIN_BLUR_SCORE:
        warnings.append("image_blurry")

    if brightness_score < MIN_BRIGHTNESS:
        warnings.append("image_too_dark")

    if brightness_score > MAX_BRIGHTNESS:
        warnings.append("image_too_bright")

    if edge_density < MIN_EDGE_DENSITY:
        warnings.append("vehicle_not_visible_or_low_detail")

    vehicle_visibility_status = (
        "possibly_visible" if edge_density >= MIN_EDGE_DENSITY else "not_visible_or_low_detail"
    )

    quality_status = "acceptable" if not warnings else "needs_review"

    return ImageQualityResult(
        quality_status=quality_status,
        blur_score=round(blur_score, 2),
        brightness_score=round(brightness_score, 2),
        edge_density=round(edge_density, 4),
        vehicle_visibility_status=vehicle_visibility_status,
        warnings=warnings,
    )