from io import BytesIO

from PIL import Image

from backend.app.services.upload_guardrail_service import validate_image_upload


def make_test_image(width: int = 640, height: int = 480, image_format: str = "PNG") -> bytes:
    image = Image.new("RGB", (width, height), color="white")
    buffer = BytesIO()
    image.save(buffer, format=image_format)
    return buffer.getvalue()


def test_upload_guardrail_allows_valid_png_image():
    file_bytes = make_test_image()

    result = validate_image_upload(
        filename="car.png",
        content_type="image/png",
        file_bytes=file_bytes,
    )

    assert result.allowed is True
    assert result.width == 640
    assert result.height == 480


def test_upload_guardrail_rejects_unsupported_extension():
    file_bytes = make_test_image()

    result = validate_image_upload(
        filename="car.gif",
        content_type="image/png",
        file_bytes=file_bytes,
    )

    assert result.allowed is False
    assert result.reason == "unsupported_file_extension"


def test_upload_guardrail_rejects_unsupported_mime_type():
    file_bytes = make_test_image()

    result = validate_image_upload(
        filename="car.png",
        content_type="application/octet-stream",
        file_bytes=file_bytes,
    )

    assert result.allowed is False
    assert result.reason == "unsupported_mime_type"


def test_upload_guardrail_rejects_empty_file():
    result = validate_image_upload(
        filename="car.png",
        content_type="image/png",
        file_bytes=b"",
    )

    assert result.allowed is False
    assert result.reason == "empty_file"


def test_upload_guardrail_rejects_corrupted_image():
    result = validate_image_upload(
        filename="car.png",
        content_type="image/png",
        file_bytes=b"not-real-image-content",
    )

    assert result.allowed is False
    assert result.reason == "corrupted_or_unreadable_image"


def test_upload_guardrail_rejects_low_resolution_image():
    file_bytes = make_test_image(width=320, height=240)

    result = validate_image_upload(
        filename="small-car.png",
        content_type="image/png",
        file_bytes=file_bytes,
    )

    assert result.allowed is False
    assert result.reason == "image_resolution_too_low"
    assert result.width == 320
    assert result.height == 240