from io import BytesIO

from fastapi.testclient import TestClient
from PIL import Image, ImageDraw

from backend.app.main import app


client = TestClient(app)


def make_image(width: int = 800, height: int = 600, color: str = "gray") -> bytes:
    image = Image.new("RGB", (width, height), color=color)
    draw = ImageDraw.Draw(image)

    draw.rectangle((120, 260, 680, 420), outline="black", width=8)
    draw.rectangle((220, 200, 560, 260), outline="black", width=8)
    draw.ellipse((200, 390, 300, 490), outline="black", width=8)
    draw.ellipse((500, 390, 600, 490), outline="black", width=8)

    buffer = BytesIO()
    image.save(buffer, format="PNG")
    return buffer.getvalue()


def test_image_analyze_accepts_safe_valid_image():
    file_bytes = make_image()

    response = client.post(
        "/image/analyze",
        files={"file": ("car.png", file_bytes, "image/png")},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["safe_image"] is True
    assert data["accepted_for_analysis"] in {True, False}
    assert data["width"] == 800
    assert data["height"] == 600
    assert data["quality_status"] in {"acceptable", "needs_review"}
    assert data["vehicle_visibility_status"] in {"possibly_visible", "not_visible_or_low_detail"}
    assert "Image passed safety" in data["message"]


def test_image_analyze_rejects_unsupported_file_type():
    response = client.post(
        "/image/analyze",
        files={"file": ("car.txt", b"not an image", "text/plain")},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["safe_image"] is False
    assert data["accepted_for_analysis"] is False
    assert data["safety_reason"] == "unsupported_file_extension"


def test_image_analyze_rejects_low_resolution_image():
    file_bytes = make_image(width=320, height=240)

    response = client.post(
        "/image/analyze",
        files={"file": ("small_car.png", file_bytes, "image/png")},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["safe_image"] is False
    assert data["accepted_for_analysis"] is False
    assert data["safety_reason"] == "image_resolution_too_low"
    assert data["width"] == 320
    assert data["height"] == 240


def test_image_analyze_rejects_nsfw_filename_before_analysis():
    file_bytes = make_image()

    response = client.post(
        "/image/analyze",
        files={"file": ("nsfw_car.png", file_bytes, "image/png")},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["safe_image"] is False
    assert data["accepted_for_analysis"] is False
    assert data["safety_reason"] == "filename_safety_flag"