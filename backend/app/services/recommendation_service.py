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
            "I could not find a strong match in the current demo inventory. "
            "Try increasing the budget, allowing both new and used cars, or relaxing the brand/body-type preference."
        )

    lines: list[str] = []

    if prefs.listing_type == "used":
        lines.append(
            "Based on your request, I focused on used cars. "
            "This usually gives you better value for the budget, but the tradeoff is that mileage, condition, "
            "service history, and accident history matter a lot."
        )
    elif prefs.listing_type == "new":
        lines.append(
            "Based on your request, I focused on new cars. "
            "These usually cost more, but they offer zero mileage, warranty coverage, and lower short-term maintenance risk."
        )
    elif prefs.listing_type == "both":
        lines.append(
            "I compared both new and used options. "
            "Used cars may give stronger value, while new cars offer warranty and zero-mileage peace of mind."
        )
    else:
        lines.append(
            "Here are the strongest matches I found from the current demo inventory."
        )

    if prefs.budget_max:
        lines.append(f"Budget target: around ${prefs.budget_max:,.0f}.")

    if prefs.use_case:
        lines.append(f"Main use case detected: {prefs.use_case}.")

    if prefs.priorities:
        lines.append(f"Priorities detected: {', '.join(prefs.priorities)}.")

    lines.append("")
    lines.append("Top matches:")

    for index, car in enumerate(cars, start=1):
        reason_parts = []

        if prefs.budget_max and car.price_usd <= prefs.budget_max:
            reason_parts.append("fits your budget")
        elif prefs.budget_max and car.price_usd <= prefs.budget_max * 1.15:
            reason_parts.append("slightly above budget but close enough to consider")

        if car.make in RELIABLE_BRANDS:
            reason_parts.append("strong reliability reputation")

        if prefs.use_case == "city" and car.body_type in ["Hatchback", "Sedan"]:
            reason_parts.append("practical size for city driving")

        if prefs.use_case == "family" and car.body_type == "SUV":
            reason_parts.append("better space for family use")

        if car.is_new:
            reason_parts.append("zero mileage")
            if car.warranty_years:
                reason_parts.append(f"{car.warranty_years:g}-year warranty")
        else:
            if car.mileage_km is not None:
                if car.mileage_km <= 80000:
                    reason_parts.append("relatively low mileage")
                elif car.mileage_km <= 120000:
                    reason_parts.append("acceptable mileage range")
                else:
                    reason_parts.append("higher mileage, needs careful inspection")
            reason_parts.append("lower entry price than a new equivalent")

        reason = ", ".join(reason_parts) if reason_parts else "reasonable match for your request"

        mileage_text = "0 km" if car.is_new else (
            f"{car.mileage_km:,} km" if car.mileage_km is not None else "mileage not listed"
        )

        warranty_text = ""
        if car.is_new and car.warranty_years:
            warranty_text = f", warranty: {car.warranty_years:g} years"

        lines.append(
            f"{index}. {car.year} {car.make} {car.model} ({car.listing_type}) — "
            f"${car.price_usd:,.0f}, {mileage_text}, {car.body_type}, "
            f"{car.fuel}, {car.transmission}{warranty_text}. "
            f"Why it fits: {reason}."
        )

    lines.append("")
    lines.append(
        "My advice: shortlist 2–3 cars from these results, compare them side by side, "
        "and for any used car, verify the service history, accident history, ownership papers, and mileage before buying."
    )

    return "\n".join(lines)