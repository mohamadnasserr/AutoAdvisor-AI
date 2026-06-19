from sqlalchemy.orm import Session

from backend.app.models.db_models import Car
from backend.app.models.schemas import PreferenceExtraction


RELIABLE_BRANDS = {"Toyota", "Honda", "Kia", "Hyundai", "Nissan"}
PERFORMANCE_BRANDS = {
    "Ferrari",
    "Lamborghini",
    "Porsche",
    "BMW",
    "Mercedes-Benz",
    "Audi",
    "Nissan",
    "Chevrolet",
    "Lexus",
}
LUXURY_BRANDS = {
    "Mercedes-Benz",
    "BMW",
    "Audi",
    "Lexus",
    "Bentley",
    "Rolls-Royce",
    "Land Rover",
}
EXOTIC_BRANDS = {"Ferrari", "Lamborghini", "Bentley", "Rolls-Royce", "Porsche"}
PERFORMANCE_MODELS = {
    "488 GTB",
    "F8 Tributo",
    "Huracan",
    "911",
    "AMG GT",
    "G63 AMG",
    "M4",
    "RS7",
    "GT-R",
    "Corvette",
    "LC 500",
    "Aventador",
    "SF90 Stradale",
}
LUXURY_MODELS = {"Continental GT", "Ghost", "Range Rover", "S-Class", "G63 AMG", "LC 500"}
PERFORMANCE_TRIMS = {"AMG", "Competition", "Turbo S", "GT3 RS", "SVJ", "Stingray", "Assetto Fiorano", "W12"}


def _contains_any(value: str | None, markers: set[str]) -> bool:
    if not value:
        return False

    normalized = value.lower()
    return any(marker.lower() in normalized for marker in markers)


def is_performance_car(car: Car) -> bool:
    return (
        car.make in PERFORMANCE_BRANDS
        and (
            car.body_type in {"Coupe", "Convertible"}
            or _contains_any(car.model, PERFORMANCE_MODELS)
            or _contains_any(car.trim, PERFORMANCE_TRIMS)
        )
    )


def is_luxury_car(car: Car) -> bool:
    return (
        car.make in LUXURY_BRANDS
        or _contains_any(car.model, LUXURY_MODELS)
        or car.price_usd >= 70000
    )


def is_exotic_car(car: Car) -> bool:
    return (
        car.make in EXOTIC_BRANDS
        or _contains_any(car.model, {"Huracan", "Aventador", "SF90", "F8", "488"})
        or car.price_usd >= 200000
    )


def score_car(car: Car, prefs: PreferenceExtraction) -> float:
    score = 0.0

    if prefs.budget_max:
        if car.price_usd <= prefs.budget_max:
            score += 30
        elif car.price_usd <= prefs.budget_max * 1.15:
            score += 10
        else:
            score -= 20

    if prefs.budget_min:
        if car.price_usd >= prefs.budget_min:
            score += 8
        elif car.price_usd >= prefs.budget_min * 0.85:
            score += 2
        else:
            score -= 8

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

    if car.availability_status and car.availability_status.lower() == "available":
        score += 12

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

    performance_match = is_performance_car(car)
    luxury_match = is_luxury_car(car)
    exotic_match = is_exotic_car(car)

    if prefs.performance_intent:
        if performance_match:
            score += 60
        elif car.body_type in {"Coupe", "Convertible"}:
            score += 25
        elif car.price_usd < 50000 and car.make in RELIABLE_BRANDS:
            score -= 35

    if prefs.luxury_preference:
        if luxury_match:
            score += 45
        elif car.price_usd < 30000 and car.make in RELIABLE_BRANDS:
            score -= 20

    if prefs.exotic_intent:
        if exotic_match:
            score += 90
        else:
            score -= 55

        if car.price_usd >= 1_000_000:
            score += 100
        elif car.price_usd >= 700000:
            score += 55
        elif car.price_usd >= 200000:
            score += 30
        elif car.price_usd < 70000:
            score -= 80

    if prefs.budget_min and prefs.budget_min >= 1_000_000:
        if car.price_usd >= prefs.budget_min:
            score += 120
        elif car.price_usd >= prefs.budget_min * 0.7:
            score += 45
        else:
            score -= 70

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

    high_end_request = bool(
        prefs.performance_intent
        or prefs.luxury_preference
        or prefs.exotic_intent
        or (prefs.budget_min is not None and prefs.budget_min >= 100000)
    )

    if prefs.budget_min:
        minimum_query = query.filter(Car.price_usd >= prefs.budget_min)
        available_minimum_candidates = (
            minimum_query.filter(Car.availability_status == "available").limit(200).all()
        )
        minimum_candidates = (
            available_minimum_candidates
            if len(available_minimum_candidates) >= limit
            else minimum_query.limit(200).all()
        )
        if len(minimum_candidates) >= limit or high_end_request:
            candidates = minimum_candidates
        else:
            available_candidates = query.filter(Car.availability_status == "available").limit(200).all()
            candidates = available_candidates if len(available_candidates) >= limit else query.limit(200).all()
    else:
        available_limit = 200 if high_end_request else 50
        available_candidates = query.filter(Car.availability_status == "available").limit(available_limit).all()
        candidates = available_candidates if len(available_candidates) >= limit else query.limit(available_limit).all()

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

    if prefs.listing_type == "used" and prefs.budget_min and prefs.budget_max:
        lines.append(
            f"Here are some used cars in the ${prefs.budget_min:,.0f} to "
            f"${prefs.budget_max:,.0f} range. "
            "This usually gives you better value for the budget, but the tradeoff is that mileage, condition, "
            "service history, and accident history matter a lot."
        )
    elif prefs.style_preference == "exotic":
        lines.append(
            "I focused on exotic and ultra-premium cars from the curated demo inventory. "
            "These matches prioritize high-end brands, special performance models, and premium positioning."
        )
    elif prefs.style_preference == "performance":
        lines.append(
            "I focused on performance-oriented cars from the curated demo inventory. "
            "These matches prioritize sporty models, coupes, and enthusiast-focused trims."
        )
    elif prefs.style_preference == "luxury":
        lines.append(
            "I focused on premium and luxury cars from the curated demo inventory. "
            "These matches prioritize comfort, brand positioning, and higher-end features."
        )
    elif prefs.listing_type == "used":
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

    if prefs.budget_min and prefs.budget_max:
        lines.append(
            f"Budget target: ${prefs.budget_min:,.0f} to ${prefs.budget_max:,.0f}."
        )
    elif prefs.budget_min:
        lines.append(f"Budget target: above ${prefs.budget_min:,.0f}.")
    elif prefs.budget_max:
        lines.append(f"Budget target: around ${prefs.budget_max:,.0f}.")

    if prefs.use_case:
        lines.append(f"Main use case detected: {prefs.use_case}.")

    if prefs.priorities:
        lines.append(f"Priorities detected: {', '.join(prefs.priorities)}.")

    lines.append("")
    lines.append("Top matches:")

    for index, car in enumerate(cars, start=1):
        reason_parts = []

        if (
            prefs.budget_min
            and prefs.budget_max
            and prefs.budget_min <= car.price_usd <= prefs.budget_max
        ):
            reason_parts.append("fits your requested budget range")
        elif prefs.budget_min and not prefs.budget_max and car.price_usd >= prefs.budget_min:
            reason_parts.append("matches your lower-budget preference")
        elif prefs.budget_min and not prefs.budget_max and car.price_usd >= prefs.budget_min * 0.85:
            reason_parts.append("near your requested lower budget")
        elif prefs.budget_max and car.price_usd <= prefs.budget_max:
            reason_parts.append("fits your budget")
        elif prefs.budget_max and car.price_usd <= prefs.budget_max * 1.15:
            reason_parts.append("slightly above budget but close enough to consider")

        if car.make in RELIABLE_BRANDS:
            reason_parts.append("strong reliability reputation")

        if prefs.use_case == "city" and car.body_type in ["Hatchback", "Sedan"]:
            reason_parts.append("practical size for city driving")

        if prefs.use_case == "family" and car.body_type == "SUV":
            reason_parts.append("better space for family use")

        if prefs.performance_intent and is_performance_car(car):
            reason_parts.append("performance-oriented model")

        if prefs.luxury_preference and is_luxury_car(car):
            reason_parts.append("premium/luxury positioning")

        if prefs.exotic_intent and is_exotic_car(car):
            reason_parts.append("exotic or ultra-premium match")

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
