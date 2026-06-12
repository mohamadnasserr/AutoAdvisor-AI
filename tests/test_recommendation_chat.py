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


def test_chat_comparison_requires_at_least_two_inventory_models():
    cars_response = client.get("/cars")
    cars_data = cars_response.json()

    first_car = cars_data["results"][0]

    message = f"Compare {first_car['make']} {first_car['model']}"

    response = client.post(
        "/chat",
        json={"message": message},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["intent"] == "car_comparison"
    assert data["recommended_cars"] == []
    assert "I need at least 2 cars to compare" in data["answer"]


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


def test_chat_routes_comparison_intent_with_existing_inventory_models():
    cars_response = client.get("/cars")
    cars_data = cars_response.json()

    first_car = cars_data["results"][0]
    second_car = cars_data["results"][1]

    message = (
        f"Compare {first_car['make']} {first_car['model']} "
        f"and {second_car['make']} {second_car['model']}"
    )

    response = client.post(
        "/chat",
        json={"message": message},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["intent"] == "car_comparison"
    assert "Here is a structured comparison" in data["answer"]
    assert len(data["recommended_cars"]) == 2

    returned_ids = {car["id"] for car in data["recommended_cars"]}
    expected_ids = {first_car["id"], second_car["id"]}

    assert returned_ids == expected_ids


def test_chat_routes_image_analysis_intent():
    response = client.post(
        "/chat",
        json={"message": "I want to upload a car image and estimate its price"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["intent"] == "image_analysis"
    assert "Image-assisted price estimation" in data["answer"]

def test_chat_asks_clarification_when_listing_type_missing():
    response = client.post(
        "/chat",
        json={"message": "I want a car for $10,000 in Lebanon"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["intent"] == "car_recommendation"
    assert data["extracted_preferences"]["budget_max"] == 10000
    assert data["extracted_preferences"]["listing_type"] is None
    assert data["recommended_cars"] == []
    assert "Do you prefer a used car, a new car, or are you open to both" in data["answer"]
    assert "used cars are usually the more realistic option" in data["answer"]



def test_chat_price_check_returns_fair_price_range():
    payload = {
        "message": "Is a 2018 Hyundai i20 with 60000 km petrol manual asking $8500 overpriced?",
        "session_id": "price-check-test",
    }

    response = client.post("/chat", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["intent"] == "price_check"
    assert "Used-car fair price estimate" in data["answer"]
    assert "Fair range" in data["answer"]
    assert "Verdict" in data["answer"]
    assert "$8,500" in data["answer"]


def test_chat_price_check_asks_for_missing_fields():
    payload = {
        "message": "Is this car overpriced?",
        "session_id": "price-check-missing-fields-test",
    }

    response = client.post("/chat", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["intent"] == "price_check"
    assert "Missing fields" in data["answer"]
    assert "brand" in data["answer"]
    assert "model" in data["answer"]

def test_chat_general_advice_uses_rag_sources():
    payload = {
        "message": "What should I check before buying a used car?",
        "session_id": "rag-general-advice-test",
    }

    response = client.post("/chat", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["intent"] == "general_advice"
    assert "Based on the AutoAdvisor knowledge base" in data["answer"]
    assert "Sources:" in data["answer"]
    assert "local://rag_docs/" in data["answer"]