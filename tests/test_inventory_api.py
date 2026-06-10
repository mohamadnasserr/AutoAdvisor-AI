from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_health_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "ok"
    assert "app" in data


def test_list_cars_returns_seeded_inventory():
    response = client.get("/cars")

    assert response.status_code == 200

    data = response.json()
    assert "results" in data
    assert "count" in data
    assert data["count"] >= 1


def test_get_car_by_id_returns_one_car():
    cars_response = client.get("/cars")
    cars_data = cars_response.json()

    first_car_id = cars_data["results"][0]["id"]

    response = client.get(f"/cars/{first_car_id}")

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == first_car_id
    assert "make" in data
    assert "model" in data
    assert "listing_type" in data


def test_get_missing_car_returns_404():
    response = client.get("/cars/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Car not found"


def test_search_cars_by_budget_and_listing_type():
    response = client.get(
        "/search/cars",
        params={
            "budget_max": 10000,
            "listing_type": "used",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert "results" in data
    assert "count" in data

    for car in data["results"]:
        assert car["price_usd"] <= 10000
        assert car["listing_type"] == "used"


def test_search_cars_by_new_listing_type():
    response = client.get(
        "/search/cars",
        params={
            "listing_type": "new",
        },
    )

    assert response.status_code == 200

    data = response.json()

    for car in data["results"]:
        assert car["listing_type"] == "new"
        assert car["is_new"] is True


def test_search_cars_supports_nullable_mileage_for_new_cars():
    response = client.get(
        "/search/cars",
        params={
            "listing_type": "new",
        },
    )

    assert response.status_code == 200

    data = response.json()

    for car in data["results"]:
        assert "mileage_km" in car
        assert "warranty_years" in car