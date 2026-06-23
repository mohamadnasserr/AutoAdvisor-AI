import pytest
from fastapi.testclient import TestClient

from backend.app.db.database import SessionLocal
from backend.app.main import app
from backend.app.models.db_models import Car, Dealership
from backend.app.services.dealer_auth_service import seed_demo_dealer_users


client = TestClient(app)


@pytest.fixture(scope="module", autouse=True)
def ensure_demo_dealer_users():
    db = SessionLocal()
    try:
        seed_demo_dealer_users(db)
    finally:
        db.close()


def login(email: str, password: str = "demo123") -> dict:
    response = client.post(
        "/dealer/auth/login",
        json={"email": email, "password": password},
    )
    assert response.status_code == 200
    return response.json()


def bearer_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def car_for_dealership(dealership_name: str) -> Car:
    db = SessionLocal()
    try:
        car = (
            db.query(Car)
            .join(Dealership, Car.dealer_id == Dealership.id)
            .filter(Dealership.name == dealership_name)
            .order_by(Car.id.asc())
            .first()
        )
        assert car is not None
        db.expunge(car)
        return car
    finally:
        db.close()


def test_dealer_login_succeeds_for_seeded_demo_user():
    data = login("beirut@autoadvisor.demo")

    assert data["access_token"]
    assert data["token_type"] == "bearer"
    assert data["dealer_user"]["email"] == "beirut@autoadvisor.demo"
    assert data["dealer_user"]["dealership_name"] == "Beirut Auto Hub"
    assert data["dealer_user"]["role"] == "dealer_admin"


def test_dealer_login_rejects_wrong_password():
    response = client.post(
        "/dealer/auth/login",
        json={
            "email": "beirut@autoadvisor.demo",
            "password": "wrong-password",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid dealer email or password."


def test_dealer_profile_requires_token_and_returns_profile_with_token():
    unauthorized = client.get("/dealer/auth/me")
    assert unauthorized.status_code == 401

    login_data = login("jounieh@autoadvisor.demo")
    response = client.get(
        "/dealer/auth/me",
        headers=bearer_headers(login_data["access_token"]),
    )

    assert response.status_code == 200
    assert response.json()["email"] == "jounieh@autoadvisor.demo"
    assert response.json()["dealership_name"] == "Cedar Motors"


def test_authenticated_dealer_leads_requires_token():
    response = client.get("/dealer/me/leads")

    assert response.status_code == 401
    assert response.json()["detail"] == "Dealer authentication required."


def test_dealer_accounts_only_see_leads_for_their_own_dealership():
    beirut_login = login("beirut@autoadvisor.demo")
    tripoli_login = login("tripoli@autoadvisor.demo")
    beirut_profile = beirut_login["dealer_user"]
    tripoli_profile = tripoli_login["dealer_user"]
    beirut_car = car_for_dealership("Beirut Auto Hub")

    create_response = client.post(
        "/dealer/leads",
        json={
            "selected_car_id": beirut_car.id,
            "customer_name": "Tenant Isolation Buyer",
            "customer_phone": "+961-1-000222",
            "customer_email": "tenant-isolation@example.invalid",
            "preferred_contact_method": "email",
            "budget": beirut_car.price_usd,
            "user_location": "Beirut",
            "notes": "Visible only to the Beirut dealership account.",
        },
    )
    assert create_response.status_code == 200
    created_lead_id = create_response.json()["lead_id"]

    beirut_response = client.get(
        "/dealer/me/leads",
        headers=bearer_headers(beirut_login["access_token"]),
    )
    tripoli_response = client.get(
        "/dealer/me/leads",
        headers=bearer_headers(tripoli_login["access_token"]),
    )

    assert beirut_response.status_code == 200
    assert tripoli_response.status_code == 200
    beirut_leads = beirut_response.json()
    tripoli_leads = tripoli_response.json()
    assert created_lead_id in {lead["lead_id"] for lead in beirut_leads}
    assert created_lead_id not in {lead["lead_id"] for lead in tripoli_leads}
    assert all(
        lead["dealership_id"] == beirut_profile["dealership_id"]
        for lead in beirut_leads
    )
    assert all(
        lead["dealership_id"] == tripoli_profile["dealership_id"]
        for lead in tripoli_leads
    )
