from io import BytesIO

from PIL import Image, ImageDraw, ImageFilter

from backend.app.services.image_quality_service import analyze_image_quality


def make_image(width: int = 800, height: int = 600, color: str = "white") -> bytes:
    image = Image.new("RGB", (width, height), color=color)
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def make_detailed_image() -> bytes:
    image = Image.new("RGB", (800, 600), color="gray")
    draw = ImageDraw.Draw(image)

    draw.rectangle((120, 260, 680, 420), outline="black", width=8)
    draw.rectangle((220, 200, 560, 260), outline="black", width=8)
    draw.ellipse((200, 390, 300, 490), outline="black", width=8)
    draw.ellipse((500, 390, 600, 490), outline="black", width=8)
    draw.line((120, 260, 220, 200), fill="black", width=8)
    draw.line((560, 200, 680, 260), fill="black", width=8)

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def make_blurry_image() -> bytes:
    image = Image.new("RGB", (800, 600), color="gray")
    draw = ImageDraw.Draw(image)
    draw.rectangle((120, 260, 680, 420), outline="black", width=8)
    image = image.filter(ImageFilter.GaussianBlur(radius=10))

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_image_quality_accepts_detailed_normal_image():
    file_bytes = make_detailed_image()

    result = analyze_image_quality(file_bytes)

    assert result.blur_score >= 0
    assert result.brightness_score >= 0
    assert result.edge_density >= 0
    assert result.vehicle_visibility_status == "possibly_visible"
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


def test_image_quality_flags_low_detail_blank_image():
    file_bytes = make_image(color="gray")

    result = analyze_image_quality(file_bytes)

    assert result.quality_status == "needs_review"
    assert result.vehicle_visibility_status == "not_visible_or_low_detail"
    assert "vehicle_not_visible_or_low_detail" in result.warnings