from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_used_car_price_estimator_returns_prediction_range():
    payload = {
        "brand": "Hyundai",
        "model": "i20",
        "vehicle_age": 5,
        "km_driven": 60000,
        "seller_type": "Dealer",
        "fuel_type": "Petrol",
        "transmission_type": "Manual",
        "mileage": 18.0,
        "engine": 1197.0,
        "max_power": 82.0,
        "seats": 5,
    }

    response = client.post("/price/used-car", json=payload)

    assert response.status_code == 200

    data = response.json()

    assert data["estimated_price_usd"] > 0
    assert data["ml_estimated_price_usd"] > 0
    assert data["low_estimate_usd"] > 0
    assert data["high_estimate_usd"] > data["low_estimate_usd"]
    assert data["low_estimate_usd"] <= data["estimated_price_usd"] <= data["high_estimate_usd"]
    assert data["fair_price_low_usd"] == data["low_estimate_usd"]
    assert data["fair_price_high_usd"] == data["high_estimate_usd"]
    assert data["currency"] == "USD"
    assert data["model_mae_usd"] is not None
    assert data["model_r2"] is not None
    assert data["calibration_note"]
    assert "inventory" in data["calibration_note"].lower()
    assert "used cars only" in data["disclaimer"]


def test_used_car_price_estimator_rejects_missing_required_fields():
    payload = {
        "brand": "Toyota",
        "model": "Corolla",
    }

    response = client.post("/price/used-car", json=payload)

    assert response.status_code == 422
