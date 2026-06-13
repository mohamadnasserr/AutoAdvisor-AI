from dataclasses import dataclass
from io import BytesIO
from pathlib import Path

from PIL import Image, UnidentifiedImageError


ALLOWED_IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
ALLOWED_IMAGE_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}
MAX_IMAGE_UPLOAD_BYTES = 5 * 1024 * 1024
MIN_IMAGE_WIDTH = 640
MIN_IMAGE_HEIGHT = 480


@dataclass
class UploadGuardrailResult:
    allowed: bool
    reason: str | None = None
    safe_response: str | None = None
    width: int | None = None
    height: int | None = None


def validate_image_upload(
    filename: str,
    content_type: str | None,
    file_bytes: bytes,
) -> UploadGuardrailResult:
    extension = Path(filename).suffix.lower()

    if extension not in ALLOWED_IMAGE_EXTENSIONS:
        return UploadGuardrailResult(
            allowed=False,
            reason="unsupported_file_extension",
            safe_response=(
                "Unsupported image file type. Please upload a JPG, JPEG, PNG, or WEBP image."
            ),
        )

    if content_type not in ALLOWED_IMAGE_MIME_TYPES:
        return UploadGuardrailResult(
            allowed=False,
            reason="unsupported_mime_type",
            safe_response=(
                "Unsupported image MIME type. Please upload a valid JPG, PNG, or WEBP image."
            ),
        )

    if len(file_bytes) == 0:
        return UploadGuardrailResult(
            allowed=False,
            reason="empty_file",
            safe_response="The uploaded file is empty. Please upload a valid car image.",
        )

    if len(file_bytes) > MAX_IMAGE_UPLOAD_BYTES:
        return UploadGuardrailResult(
            allowed=False,
            reason="file_too_large",
            safe_response="The uploaded image is too large. Please upload an image up to 5 MB.",
        )

    try:
        image = Image.open(BytesIO(file_bytes))
        image.verify()

        image = Image.open(BytesIO(file_bytes))
        width, height = image.size

    except (UnidentifiedImageError, OSError, ValueError):
        return UploadGuardrailResult(
            allowed=False,
            reason="corrupted_or_unreadable_image",
            safe_response=(
                "The uploaded file could not be read as a valid image. Please upload a clear JPG, PNG, or WEBP car image."
            ),
        )

    if width < MIN_IMAGE_WIDTH or height < MIN_IMAGE_HEIGHT:
        return UploadGuardrailResult(
            allowed=False,
            reason="image_resolution_too_low",
            safe_response=(
                f"The image resolution is too low. Minimum required resolution is "
                f"{MIN_IMAGE_WIDTH}x{MIN_IMAGE_HEIGHT}."
            ),
            width=width,
            height=height,
        )

    return UploadGuardrailResult(
        allowed=True,
        width=width,
        height=height,
    )