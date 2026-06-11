from sqlalchemy.orm import Session

from backend.app.models.db_models import Car
from backend.app.models.schemas import CarComparisonItem


RELIABLE_BRANDS = {"Toyota", "Honda", "Kia", "Hyundai", "Nissan"}


def get_best_use_case(car: Car) -> str:
    if car.body_type == "Hatchback":
        return "City driving, easy parking, fuel-conscious daily use"

    if car.body_type == "Sedan":
        return "Daily commuting, first car, balanced comfort and practicality"

    if car.body_type == "SUV":
        return "Family use, space, comfort, mixed road conditions"

    if car.body_type == "Pickup":
        return "Utility, work use, carrying cargo"

    return "General use"


def build_strengths(car: Car) -> list[str]:
    strengths: list[str] = []

    if car.make in RELIABLE_BRANDS:
        strengths.append("Reliable brand reputation")

    if car.is_new:
        strengths.append("Zero mileage")
        if car.warranty_years:
            strengths.append(f"{car.warranty_years:g}-year warranty")
        strengths.append("Lower short-term maintenance risk")
    else:
        strengths.append("Lower entry price than most new cars")

        if car.mileage_km is not None:
            if car.mileage_km <= 80000:
                strengths.append("Relatively low mileage")
            elif car.mileage_km <= 120000:
                strengths.append("Acceptable mileage for age")

    if car.body_type in ["Hatchback", "Sedan"]:
        strengths.append("Practical for city driving")

    if car.body_type == "SUV":
        strengths.append("Practical for family use and cargo space")

    if car.fuel == "Hybrid":
        strengths.append("Better fuel economy potential")

    return strengths or ["Reasonable all-around option"]


def build_risks(car: Car) -> list[str]:
    risks: list[str] = []

    if car.is_new:
        risks.append("Higher purchase price than used alternatives")
        risks.append("Depreciates faster in the first years")
    else:
        risks.append("Requires mechanical inspection before purchase")
        risks.append("Service history and accident history must be verified")

        if car.mileage_km is not None and car.mileage_km > 120000:
            risks.append("Higher mileage, inspect carefully")

        if car.condition and car.condition.lower() in ["fair", "poor"]:
            risks.append("Condition is not ideal")

    if car.make in {"BMW", "Mercedes-Benz"}:
        risks.append("Potentially higher maintenance and parts cost")

    return risks


def calculate_verdict_score(car: Car) -> float:
    score = 0.0

    if car.make in RELIABLE_BRANDS:
        score += 20

    if car.is_new:
        score += 20
        if car.warranty_years:
            score += min(car.warranty_years * 3, 10)
    else:
        score += 8

        if car.mileage_km is not None:
            if car.mileage_km <= 80000:
                score += 20
            elif car.mileage_km <= 120000:
                score += 10
            else:
                score -= 5

    if car.body_type in ["Hatchback", "Sedan", "SUV"]:
        score += 10

    if car.condition == "Good":
        score += 10

    if car.condition == "New":
        score += 15

    # Cheaper cars get a small value advantage.
    if car.price_usd <= 10000:
        score += 15
    elif car.price_usd <= 18000:
        score += 10
    elif car.price_usd <= 30000:
        score += 5

    if car.make in {"BMW", "Mercedes-Benz"} and not car.is_new:
        score -= 10

    return score


def compare_cars_by_ids(db: Session, car_ids: list[int]) -> tuple[list[CarComparisonItem], str, int | None]:
    cars = (
        db.query(Car)
        .filter(Car.id.in_(car_ids))
        .all()
    )

    found_ids = {car.id for car in cars}
    missing_ids = [car_id for car_id in car_ids if car_id not in found_ids]

    if missing_ids:
        raise ValueError(f"Cars not found: {missing_ids}")

    ordered_cars = sorted(cars, key=lambda car: car_ids.index(car.id))

    comparison_items: list[CarComparisonItem] = []

    for car in ordered_cars:
        title = f"{car.year} {car.make} {car.model}"

        comparison_items.append(
            CarComparisonItem(
                id=car.id,
                title=title,
                listing_type=car.listing_type,
                is_new=car.is_new,
                price_usd=car.price_usd,
                year=car.year,
                mileage_km=car.mileage_km,
                body_type=car.body_type,
                fuel=car.fuel,
                transmission=car.transmission,
                condition=car.condition,
                warranty_years=car.warranty_years,
                strengths=build_strengths(car),
                risks=build_risks(car),
                best_use_case=get_best_use_case(car),
                verdict_score=calculate_verdict_score(car),
            )
        )

    best_item = max(comparison_items, key=lambda item: item.verdict_score, default=None)

    if best_item is None:
        return comparison_items, "No cars were available for comparison.", None

    final_verdict = (
        f"Best overall option: {best_item.title}. "
        f"It has the strongest balance of value, reliability, mileage/warranty profile, "
        f"and practical use case among the selected cars."
    )

    return comparison_items, final_verdict, best_item.id