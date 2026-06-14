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
    assert data["dominant_color"] in {
        "black",
        "white",
        "silver",
        "gray",
        "red",
        "blue",
        "green",
        "yellow",
        "brown",
        "orange",
        "unknown",
    }
    assert data["estimated_body_type"] in {
        "sedan_or_coupe_like",
        "suv_or_hatchback_like",
        "unknown",
    }
    assert data["analysis_status"] in {
        "metadata_estimated",
        "needs_better_image_before_metadata_extraction",
    }


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
    assert data["dominant_color"] is None
    assert data["estimated_body_type"] is None
    assert data["analysis_status"] is None


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
    assert data["dominant_color"] is None
    assert data["estimated_body_type"] is None
    assert data["analysis_status"] is None


def test_image_similar_cars_returns_inventory_matches_without_upload():
    inventory_response = client.get("/cars")
    inventory_ids = {
        car["id"] for car in inventory_response.json()["results"]
    }

    response = client.post(
        "/image/similar-cars",
        json={
            "make": "Toyota",
            "model": "Corolla",
            "year": 2018,
            "mileage_km": 90000,
            "body_type": "Sedan",
            "fuel": "Petrol",
            "transmission": "Automatic",
            "budget_max": 12000,
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["query_summary"]
    assert data["explanation"]
    assert 1 <= len(data["similar_cars"]) <= 5
    assert all(car["id"] in inventory_ids for car in data["similar_cars"])
    assert all(car["availability_status"] != "sold" for car in data["similar_cars"])


def test_image_similar_cars_defaults_to_used_inventory():
    response = client.post(
        "/image/similar-cars",
        json={"body_type": "SUV", "fuel": "Petrol"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["similar_cars"]
    assert all(car["listing_type"] == "used" for car in data["similar_cars"])
