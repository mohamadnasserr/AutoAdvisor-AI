from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_create_dealer_lead_for_existing_car():
    cars_response = client.get("/cars")

    assert cars_response.status_code == 200

    cars_payload = cars_response.json()

    if isinstance(cars_payload, dict):
        cars = cars_payload.get("results", [])
    else:
        cars = cars_payload

    assert len(cars) > 0

    selected_car = cars[0]

    payload = {
        "selected_car_id": selected_car["id"],
        "user_location": "Beirut",
        "preferred_contact_method": "phone",
        "budget": selected_car["price_usd"],
    }

    response = client.post("/dealer/leads", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["lead_id"] > 0
    assert data["selected_car_id"] == selected_car["id"]
    assert data["message_draft"]
    assert "AutoAdvisor AI" in data["message_draft"]
    assert "confirm availability" in data["message_draft"]
    assert data["status"] == "draft_created"


def test_create_dealer_lead_for_missing_car_returns_404():
    payload = {
        "selected_car_id": 999999,
        "user_location": "Beirut",
        "preferred_contact_method": "phone",
    }

    response = client.post("/dealer/leads", json=payload)

    assert response.status_code == 404
    assert response.json()["detail"] == "Selected car not found."