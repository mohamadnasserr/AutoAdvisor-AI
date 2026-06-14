from dataclasses import dataclass
from io import BytesIO

import numpy as np
from PIL import Image


@dataclass
class VehicleImageMetadata:
    dominant_color: str
    estimated_body_type: str
    analysis_status: str


def _nearest_color_name(rgb: tuple[int, int, int]) -> str:
    color_map = {
        "black": (25, 25, 25),
        "white": (235, 235, 235),
        "silver": (180, 180, 180),
        "gray": (120, 120, 120),
        "red": (180, 35, 35),
        "blue": (40, 80, 180),
        "green": (45, 130, 70),
        "yellow": (220, 190, 45),
        "brown": (120, 75, 40),
        "orange": (220, 110, 35),
    }

    rgb_array = np.array(rgb)

    nearest_name = "unknown"
    nearest_distance = float("inf")

    for name, reference_rgb in color_map.items():
        distance = np.linalg.norm(rgb_array - np.array(reference_rgb))
        if distance < nearest_distance:
            nearest_distance = distance
            nearest_name = name

    return nearest_name


def estimate_dominant_color(file_bytes: bytes) -> str:
    image = Image.open(BytesIO(file_bytes)).convert("RGB")
    image = image.resize((128, 128))

    pixels = np.array(image).reshape(-1, 3)

    # Ignore very bright background-like pixels and very dark shadow-like pixels.
    brightness = pixels.mean(axis=1)
    filtered_pixels = pixels[(brightness > 35) & (brightness < 245)]

    if len(filtered_pixels) == 0:
        filtered_pixels = pixels

    median_rgb = tuple(np.median(filtered_pixels, axis=0).astype(int).tolist())
    return _nearest_color_name(median_rgb)


def estimate_body_type_from_shape(width: int | None, height: int | None) -> str:
    if not width or not height:
        return "unknown"

    aspect_ratio = width / height

    if aspect_ratio >= 1.55:
        return "sedan_or_coupe_like"

    if 1.25 <= aspect_ratio < 1.55:
        return "suv_or_hatchback_like"

    return "unknown"


def extract_vehicle_image_metadata(
    file_bytes: bytes,
    width: int | None,
    height: int | None,
    accepted_for_analysis: bool,
) -> VehicleImageMetadata:
    if not accepted_for_analysis:
        return VehicleImageMetadata(
            dominant_color="unknown",
            estimated_body_type="unknown",
            analysis_status="needs_better_image_before_metadata_extraction",
        )

    dominant_color = estimate_dominant_color(file_bytes)
    estimated_body_type = estimate_body_type_from_shape(width, height)

    return VehicleImageMetadata(
        dominant_color=dominant_color,
        estimated_body_type=estimated_body_type,
        analysis_status="metadata_estimated",
    )