from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_chat_recommends_used_city_car_under_budget():
    response = client.post(
        "/chat",
        json={"message": "I need a reliable used city car under $10,000 in Lebanon"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["intent"] == "car_recommendation"
    assert data["extracted_preferences"]["budget_max"] == 10000
    assert data["extracted_preferences"]["listing_type"] == "used"
    assert data["extracted_preferences"]["use_case"] == "city"
    assert len(data["recommended_cars"]) >= 1

    for car in data["recommended_cars"]:
        assert car["listing_type"] == "used"
        assert car["price_usd"] <= 11500


def test_chat_can_recommend_new_car_option():
    response = client.post(
        "/chat",
        json={"message": "I want a brand new small city car in Lebanon"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["intent"] == "car_recommendation"
    assert data["extracted_preferences"]["listing_type"] == "new"
    assert len(data["recommended_cars"]) >= 1

    for car in data["recommended_cars"]:
        assert car["listing_type"] == "new"
        assert car["is_new"] is True


def test_chat_handles_new_or_used_request():
    response = client.post(
        "/chat",
        json={"message": "I am open to new or used cars, budget around $18,000"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["intent"] == "car_recommendation"
    assert data["extracted_preferences"]["listing_type"] == "both"
    assert len(data["recommended_cars"]) >= 1


def test_chat_routes_comparison_intent():
    response = client.post(
        "/chat",
        json={"message": "Compare Toyota Corolla and Honda Civic for a first car"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["intent"] == "car_comparison"
    assert "Comparison workflow" in data["answer"]


def test_chat_routes_image_analysis_intent():
    response = client.post(
        "/chat",
        json={"message": "I want to upload a car image and estimate its price"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["intent"] == "image_analysis"
    assert "Image-assisted price estimation" in data["answer"]