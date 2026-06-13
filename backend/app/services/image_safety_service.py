from dataclasses import dataclass


NSFW_FILENAME_PATTERNS = [
    "nsfw",
    "nude",
    "nudity",
    "porn",
    "explicit",
    "adult",
    "sexual",
]


@dataclass
class ImageSafetyResult:
    safe_image: bool
    nsfw_score: float
    reason: str | None = None
    safe_response: str | None = None


def check_image_safety(filename: str, file_bytes: bytes) -> ImageSafetyResult:
    lowered_filename = filename.lower()

    if any(pattern in lowered_filename for pattern in NSFW_FILENAME_PATTERNS):
        return ImageSafetyResult(
            safe_image=False,
            nsfw_score=1.0,
            reason="filename_safety_flag",
            safe_response=(
                "This image was rejected by the safety gate. "
                "Please upload a safe, appropriate car image."
            ),
        )

    if not file_bytes:
        return ImageSafetyResult(
            safe_image=False,
            nsfw_score=0.0,
            reason="empty_file",
            safe_response="The uploaded file is empty. Please upload a valid car image.",
        )

    return ImageSafetyResult(
        safe_image=True,
        nsfw_score=0.0,
    )