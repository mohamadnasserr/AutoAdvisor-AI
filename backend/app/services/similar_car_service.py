from sqlalchemy.orm import Session

from backend.app.models.db_models import Car
from backend.app.models.schemas import SimilarCarsRequest


def _matches(value: str | None, requested: str | None) -> bool:
    return bool(value and requested and value.lower() == requested.lower())


def _score_car(car: Car, request: SimilarCarsRequest) -> float:
    score = 0.0

    if car.availability_status.lower() == "available":
        score += 30
    elif car.availability_status.lower() == "reserved":
        score += 5
    else:
        score -= 100

    if request.listing_type:
        score += 35 if _matches(car.listing_type, request.listing_type) else -10

    if request.make:
        score += 25 if _matches(car.make, request.make) else 0

    if request.model:
        score += 35 if _matches(car.model, request.model) else 0

    if request.body_type:
        score += 20 if _matches(car.body_type, request.body_type) else 0

    if request.fuel:
        score += 12 if _matches(car.fuel, request.fuel) else 0

    if request.transmission:
        score += 12 if _matches(car.transmission, request.transmission) else 0

    if request.year is not None:
        year_difference = abs(car.year - request.year)
        score += max(20 - (year_difference * 4), 0)

    if request.mileage_km is not None and car.mileage_km is not None:
        mileage_difference = abs(car.mileage_km - request.mileage_km)
        score += max(18 - (mileage_difference / 10000 * 3), 0)

    if request.budget_max is not None:
        if car.price_usd <= request.budget_max:
            score += 25
        elif car.price_usd <= request.budget_max * 1.15:
            score += 10
        else:
            score -= min((car.price_usd - request.budget_max) / 1000, 20)

    return score


def _build_query_summary(request: SimilarCarsRequest) -> str:
    details: list[str] = []

    if request.year is not None:
        details.append(str(request.year))
    if request.make:
        details.append(request.make)
    if request.model:
        details.append(request.model)
    if request.body_type:
        details.append(request.body_type)
    if request.fuel:
        details.append(request.fuel)
    if request.transmission:
        details.append(request.transmission)
    if request.mileage_km is not None:
        details.append(f"around {request.mileage_km:,} km")
    if request.budget_max is not None:
        details.append(f"up to ${request.budget_max:,.0f}")
    if request.listing_type:
        details.append(f"{request.listing_type} listings")

    return ", ".join(details) if details else "Available used-car inventory"


def _is_close_match(car: Car, request: SimilarCarsRequest) -> bool:
    checks: list[bool] = []

    if request.listing_type:
        checks.append(_matches(car.listing_type, request.listing_type))
    if request.make:
        checks.append(_matches(car.make, request.make))
    if request.model:
        checks.append(_matches(car.model, request.model))
    if request.body_type:
        checks.append(_matches(car.body_type, request.body_type))
    if request.fuel:
        checks.append(_matches(car.fuel, request.fuel))
    if request.transmission:
        checks.append(_matches(car.transmission, request.transmission))
    if request.year is not None:
        checks.append(abs(car.year - request.year) <= 2)
    if request.mileage_km is not None and car.mileage_km is not None:
        checks.append(abs(car.mileage_km - request.mileage_km) <= 30000)
    if request.budget_max is not None:
        checks.append(car.price_usd <= request.budget_max * 1.15)

    return all(checks) if checks else True


def find_similar_cars(
    db: Session,
    request: SimilarCarsRequest,
    limit: int = 5,
) -> tuple[list[Car], str, str]:
    candidates = (
        db.query(Car)
        .filter(Car.availability_status != "sold")
        .all()
    )

    if len(candidates) < limit:
        candidates = db.query(Car).all()

    ranked = sorted(
        candidates,
        key=lambda car: (_score_car(car, request), -car.price_usd),
        reverse=True,
    )
    similar_cars = ranked[:limit]
    close_match_count = sum(
        _is_close_match(car, request) for car in similar_cars
    )

    if close_match_count == len(similar_cars):
        explanation = (
            "These are the closest available matches from the curated PostgreSQL "
            "demo inventory using the confirmed vehicle details."
        )
    else:
        explanation = (
            "Exact matches were limited, so the results include the closest available "
            "alternatives from the curated PostgreSQL demo inventory. Matching uses "
            "confirmed details, not image recognition alone."
        )

    return similar_cars, _build_query_summary(request), explanation
