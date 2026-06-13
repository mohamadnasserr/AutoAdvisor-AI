from io import BytesIO

from PIL import Image, ImageFilter

from backend.app.services.image_quality_service import analyze_image_quality


def make_image(width: int = 800, height: int = 600, color: str = "white") -> bytes:
    image = Image.new("RGB", (width, height), color=color)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def make_blurry_image() -> bytes:
    image = Image.new("RGB", (800, 600), color="white")
    image = image.filter(ImageFilter.GaussianBlur(radius=10))
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_image_quality_accepts_clear_normal_image():
    file_bytes = make_image(color="gray")

    result = analyze_image_quality(file_bytes)

    assert result.quality_status in {"acceptable", "needs_review"}
    assert result.blur_score >= 0
    assert result.brightness_score >= 0
    assert isinstance(result.warnings, list)


def test_image_quality_flags_dark_image():
    file_bytes = make_image(color="black")

    result = analyze_image_quality(file_bytes)

    assert result.quality_status == "needs_review"
    assert "image_too_dark" in result.warnings


def test_image_quality_flags_too_bright_image():
    file_bytes = make_image(color="white")

    result = analyze_image_quality(file_bytes)

    assert result.quality_status == "needs_review"
    assert "image_too_bright" in result.warnings


def test_image_quality_flags_blurry_image():
    file_bytes = make_blurry_image()

    result = analyze_image_quality(file_bytes)

    assert result.quality_status == "needs_review"
    assert "image_blurry" in result.warnings