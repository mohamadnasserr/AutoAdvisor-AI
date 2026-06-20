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


def test_create_dealer_lead_stores_buyer_contact_details():
    cars_response = client.get("/cars")
    selected_car = cars_response.json()["results"][0]

    payload = {
        "selected_car_id": selected_car["id"],
        "customer_name": "Demo Buyer",
        "customer_phone": "+961-1-000000",
        "customer_email": "buyer@example.invalid",
        "user_location": "Beirut",
        "preferred_contact_method": "email",
        "budget": selected_car["price_usd"],
        "notes": "Interested in arranging a demo inspection.",
    }

    response = client.post("/dealer/leads", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["selected_car_id"] == selected_car["id"]
    assert data["customer_name"] == payload["customer_name"]
    assert data["customer_phone"] == payload["customer_phone"]
    assert data["customer_email"] == payload["customer_email"]
    assert data["status"] == "draft_created"


def test_get_dealer_leads_returns_created_lead_with_car_and_dealer_details():
    cars_response = client.get("/cars")
    selected_car = cars_response.json()["results"][0]
    payload = {
        "selected_car_id": selected_car["id"],
        "customer_name": "Dashboard Demo Buyer",
        "customer_phone": "+961-1-000111",
        "customer_email": "dashboard-buyer@example.invalid",
        "preferred_contact_method": "email",
        "budget": selected_car["price_usd"],
        "user_location": "Beirut",
        "notes": "Dashboard readback test.",
    }

    create_response = client.post("/dealer/leads", json=payload)
    assert create_response.status_code == 200
    created_lead_id = create_response.json()["lead_id"]

    response = client.get("/dealer/leads")
    assert response.status_code == 200

    lead = next(item for item in response.json() if item["lead_id"] == created_lead_id)
    assert lead["customer_name"] == payload["customer_name"]
    assert lead["customer_phone"] == payload["customer_phone"]
    assert lead["customer_email"] == payload["customer_email"]
    assert lead["selected_car_id"] == selected_car["id"]
    assert str(selected_car["year"]) in lead["car_title"]
    assert selected_car["make"] in lead["car_title"]
    assert lead["car_price_usd"] == selected_car["price_usd"]
    assert lead["dealership_id"] is not None
    assert lead["dealership_name"]
    assert lead["created_at"]


def test_get_dealer_leads_filters_by_dealership_and_status():
    all_response = client.get("/dealer/leads")
    assert all_response.status_code == 200
    all_leads = all_response.json()
    assert all_leads

    selected_lead = next(
        lead for lead in all_leads
        if lead["dealership_id"] is not None and lead["status"] == "draft_created"
    )
    response = client.get(
        "/dealer/leads",
        params={
            "dealer_id": selected_lead["dealership_id"],
            "status": "draft_created",
        },
    )

    assert response.status_code == 200
    filtered_leads = response.json()
    assert filtered_leads
    assert selected_lead["lead_id"] in {lead["lead_id"] for lead in filtered_leads}
    assert all(
        lead["dealership_id"] == selected_lead["dealership_id"]
        for lead in filtered_leads
    )
    assert all(lead["status"] == "draft_created" for lead in filtered_leads)


def test_get_dealerships_returns_dashboard_dropdown_options():
    response = client.get("/dealer/dealerships")

    assert response.status_code == 200
    dealerships = response.json()
    assert dealerships
    assert all(dealership["id"] > 0 for dealership in dealerships)
    assert all(dealership["name"] for dealership in dealerships)
    assert all(dealership["location"] for dealership in dealerships)
