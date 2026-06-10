from sqlalchemy.orm import Session

from backend.app.models.db_models import Car
from backend.app.models.schemas import PreferenceExtraction


RELIABLE_BRANDS = {"Toyota", "Honda", "Kia", "Hyundai", "Nissan"}


def score_car(car: Car, prefs: PreferenceExtraction) -> float:
    score = 0.0

    if prefs.budget_max:
        if car.price_usd <= prefs.budget_max:
            score += 30
        elif car.price_usd <= prefs.budget_max * 1.15:
            score += 10
        else:
            score -= 20

    if prefs.listing_type:
        if prefs.listing_type == "both":
            score += 5
        elif car.listing_type.lower() == prefs.listing_type.lower():
            score += 20

    if prefs.body_type and car.body_type.lower() == prefs.body_type.lower():
        score += 20

    if prefs.fuel and car.fuel.lower() == prefs.fuel.lower():
        score += 10

    if prefs.transmission and car.transmission.lower() == prefs.transmission.lower():
        score += 10

    if prefs.brand_preference and car.make.lower() == prefs.brand_preference.lower():
        score += 20

    if prefs.region and prefs.region.lower() in car.region.lower():
        score += 10

    if "reliability" in prefs.priorities and car.make in RELIABLE_BRANDS:
        score += 15

    if prefs.use_case == "city":
        if car.body_type in ["Hatchback", "Sedan"]:
            score += 15
        if car.mileage_km is not None and car.mileage_km < 100000:
            score += 10
        if car.is_new:
            score += 8

    if prefs.use_case == "family":
        if car.body_type == "SUV":
            score += 20

    if prefs.luxury_preference and car.make in ["BMW", "Mercedes-Benz"]:
        score += 15
        if "low maintenance" in prefs.priorities:
            score -= 15

    if car.is_new:
        score += 8
        if car.warranty_years:
            score += min(car.warranty_years * 3, 10)
    else:
        if car.mileage_km is not None:
            if car.mileage_km <= 80000:
                score += 10
            elif car.mileage_km <= 120000:
                score += 5
            else:
                score -= 5

    return score


def recommend_cars(db: Session, prefs: PreferenceExtraction, limit: int = 5) -> list[Car]:
    query = db.query(Car)

    if prefs.budget_max:
        query = query.filter(Car.price_usd <= prefs.budget_max * 1.15)

    if prefs.listing_type and prefs.listing_type != "both":
        query = query.filter(Car.listing_type == prefs.listing_type)

    if prefs.body_type:
        query = query.filter(Car.body_type.ilike(f"%{prefs.body_type}%"))

    if prefs.brand_preference:
        query = query.filter(Car.make.ilike(f"%{prefs.brand_preference}%"))

    candidates = query.limit(50).all()

    ranked = sorted(
        candidates,
        key=lambda car: score_car(car, prefs),
        reverse=True,
    )

    return ranked[:limit]


def build_recommendation_answer(cars: list[Car], prefs: PreferenceExtraction) -> str:
    if not cars:
        return (
            "I could not find a strong match in the demo inventory. "
            "Try increasing the budget or relaxing the brand/body-type preference."
        )

    lines = [
        "Here are the best matches from the Lebanon/MENA demo inventory:",
        "",
    ]

    for index, car in enumerate(cars, start=1):
        reason_parts = []

        if prefs.budget_max and car.price_usd <= prefs.budget_max:
            reason_parts.append("within budget")

        if car.make in RELIABLE_BRANDS:
            reason_parts.append("reliable brand reputation")

        if prefs.use_case == "city" and car.body_type in ["Sedan", "Hatchback"]:
            reason_parts.append("good body type for city driving")

        if prefs.use_case == "family" and car.body_type == "SUV":
            reason_parts.append("practical family option")

        if car.is_new:
            reason_parts.append("new car with zero mileage")
            if car.warranty_years:
                reason_parts.append(f"{car.warranty_years:g}-year warranty")
        else:
            reason_parts.append("used-car option with lower entry price")

        reason = ", ".join(reason_parts)

        mileage_text = "0 km" if car.is_new else f"{car.mileage_km:,} km"

        lines.append(
            f"{index}. {car.year} {car.make} {car.model} "
            f"({car.listing_type}) — ${car.price_usd:,.0f}, "
            f"{mileage_text}, {car.body_type}. Reason: {reason}."
        )

    lines.append("")
    lines.append(
        "Note: used-car prices are demo estimates and should be verified with inspection, "
        "service history, ownership papers, accident history, and real market availability."
    )

    return "\n".join(lines)