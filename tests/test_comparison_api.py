from fastapi.testclient import TestClient

from backend.app.main import app


client = TestClient(app)


def test_compare_two_cars():
    cars_response = client.get("/cars")
    cars_data = cars_response.json()

    car_ids = [car["id"] for car in cars_data["results"][:2]]

    response = client.post(
        "/compare",
        json={"car_ids": car_ids},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["compared_count"] == 2
    assert len(data["cars"]) == 2
    assert data["best_overall_car_id"] in car_ids
    assert "Best overall option" in data["final_verdict"]

    for car in data["cars"]:
        assert "title" in car
        assert "strengths" in car
        assert "risks" in car
        assert "best_use_case" in car
        assert "verdict_score" in car


def test_compare_three_to_five_cars():
    cars_response = client.get("/cars")
    cars_data = cars_response.json()

    car_ids = [car["id"] for car in cars_data["results"][:5]]

    response = client.post(
        "/compare",
        json={"car_ids": car_ids},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["compared_count"] == 5
    assert len(data["cars"]) == 5
    assert data["best_overall_car_id"] in car_ids


def test_compare_rejects_fewer_than_two_cars():
    cars_response = client.get("/cars")
    cars_data = cars_response.json()

    car_id = cars_data["results"][0]["id"]

    response = client.post(
        "/compare",
        json={"car_ids": [car_id]},
    )

    assert response.status_code == 422


def test_compare_rejects_more_than_five_cars():
    cars_response = client.get("/cars")
    cars_data = cars_response.json()

    car_ids = [car["id"] for car in cars_data["results"][:6]]

    response = client.post(
        "/compare",
        json={"car_ids": car_ids},
    )

    assert response.status_code == 422


def test_compare_missing_car_returns_404():
    response = client.post(
        "/compare",
        json={"car_ids": [1, 999999]},
    )

    assert response.status_code == 404
    assert "Cars not found" in response.json()["detail"]