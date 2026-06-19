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


def test_chat_routes_clear_used_car_shopping_request_to_recommendations():
    response = client.post(
        "/chat",
        json={
            "message": "Reliable used car under $10,000 in Beirut",
            "session_id": "recommendation-override-test",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["intent"] == "car_recommendation"
    assert data["extracted_preferences"]["listing_type"] == "used"
    assert "Based on the AutoAdvisor knowledge base" not in data["answer"]
    assert data["recommended_cars"] or "could not find a strong match" in data["answer"]


def test_chat_recommends_used_cars_for_budget_range_request():
    response = client.post(
        "/chat",
        json={
            "message": "can you show me some good used cars in the range between 5000 to 15000",
            "session_id": "budget-range-recommendation-test",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["intent"] == "car_recommendation"
    assert data["extracted_preferences"]["listing_type"] == "used"
    assert data["extracted_preferences"]["budget_min"] == 5000
    assert data["extracted_preferences"]["budget_max"] == 15000
    assert len(data["recommended_cars"]) > 0
    assert "I couldn’t find a strong match" not in data["answer"]
    assert "I could not find a strong match" not in data["answer"]
    assert "Based on the AutoAdvisor knowledge base" not in data["answer"]

    for car in data["recommended_cars"]:
        assert car["listing_type"] == "used"
        assert car["price_usd"] <= 17250


def test_chat_recommends_used_cars_for_budget_minimum_request_with_price_word():
    response = client.post(
        "/chat",
        json={
            "message": "show me some used cars more than 10000 price",
            "session_id": "budget-minimum-recommendation-test",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["intent"] == "car_recommendation"
    assert data["extracted_preferences"]["listing_type"] == "used"
    assert data["extracted_preferences"]["budget_min"] == 10000
    assert data["extracted_preferences"]["budget_max"] is None
    assert len(data["recommended_cars"]) > 0
    assert "Missing fields" not in data["answer"]
    assert "Please send something like" not in data["answer"]
    assert "2018 Hyundai i20" not in data["answer"]

    for car in data["recommended_cars"]:
        assert car["listing_type"] == "used"
        assert car["price_usd"] >= 8500


def test_chat_recommends_performance_cars_for_fast_request():
    response = client.post(
        "/chat",
        json={
            "message": "I want a fast car",
            "session_id": "performance-recommendation-test",
        },
    )

    assert response.status_code == 200

    data = response.json()
    recommended_cars = data["recommended_cars"]

    assert data["intent"] == "car_recommendation"
    assert data["extracted_preferences"]["performance_intent"] is True
    assert data["extracted_preferences"]["style_preference"] == "performance"
    assert len(recommended_cars) > 0

    performance_markers = {
        "Ferrari",
        "Lamborghini",
        "Porsche",
        "AMG GT",
        "M4",
        "RS7",
        "GT-R",
        "Corvette",
        "LC 500",
    }
    assert any(
        car["make"] in performance_markers
        or car["model"] in performance_markers
        or (car.get("trim") in performance_markers)
        for car in recommended_cars
    )
    assert recommended_cars[0]["price_usd"] >= 70000


def test_chat_recommends_high_price_exotics_for_above_one_million_request():
    response = client.post(
        "/chat",
        json={
            "message": "show me a car above one million",
            "session_id": "million-dollar-recommendation-test",
        },
    )

    assert response.status_code == 200

    data = response.json()
    recommended_cars = data["recommended_cars"]

    assert data["intent"] == "car_recommendation"
    assert data["extracted_preferences"]["budget_min"] == 1000000
    assert data["extracted_preferences"]["exotic_intent"] is True
    assert data["extracted_preferences"]["style_preference"] == "exotic"
    assert len(recommended_cars) > 0
    assert any(car["price_usd"] >= 1000000 for car in recommended_cars)
    assert recommended_cars[0]["price_usd"] >= 700000


def test_chat_recommends_ferrari_when_requested():
    response = client.post(
        "/chat",
        json={
            "message": "I want a Ferrari",
            "session_id": "ferrari-recommendation-test",
        },
    )

    assert response.status_code == 200

    data = response.json()
    recommended_cars = data["recommended_cars"]

    assert data["intent"] == "car_recommendation"
    assert data["extracted_preferences"]["brand_preference"] == "Ferrari"
    assert data["extracted_preferences"]["exotic_intent"] is True
    assert len(recommended_cars) > 0
    assert any(car["make"] == "Ferrari" for car in recommended_cars)
    assert recommended_cars[0]["make"] == "Ferrari"


def test_chat_greeting_returns_help_instead_of_rag_advice():
    response = client.post(
        "/chat",
        json={"message": "hello", "session_id": "greeting-test"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["intent"] == "greeting"
    assert "Based on the AutoAdvisor knowledge base" not in data["answer"]
    assert "AutoAdvisor AI" in data["answer"]
    assert "What are you looking for?" in data["answer"]
    assert not data["answer"].lstrip().startswith("{")


def test_chat_how_are_you_returns_greeting_without_rag():
    response = client.post(
        "/chat",
        json={"message": "how are you", "session_id": "greeting-how-are-you-test"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["intent"] == "greeting"
    assert "Based on the AutoAdvisor knowledge base" not in data["answer"]


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
    assert "ML baseline" in data["answer"]
    assert "Inventory calibration" in data["answer"]
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

def test_chat_dealer_contact_creates_inquiry_draft():
    cars_response = client.get("/cars")
    assert cars_response.status_code == 200

    cars_payload = cars_response.json()
    cars = cars_payload.get("results", []) if isinstance(cars_payload, dict) else cars_payload
    assert len(cars) > 0

    selected_car = cars[0]

    payload = {
        "message": f"Connect me with the dealer for the {selected_car['make']} {selected_car['model']}",
        "session_id": "dealer-contact-chat-test",
    }

    response = client.post("/chat", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["intent"] == "dealer_contact"
    assert "I created a draft dealer inquiry" in data["answer"]
    assert "Inquiry draft" in data["answer"]
    assert "I did not send this message automatically" in data["answer"]
