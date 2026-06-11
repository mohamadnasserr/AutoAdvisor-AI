import re
from dataclasses import dataclass

from backend.app.models.schemas import UsedCarPricePredictionRequest


KNOWN_BRANDS = [
    "Toyota",
    "Hyundai",
    "Kia",
    "Honda",
    "Nissan",
    "BMW",
    "Mercedes-Benz",
    "Mercedes",
    "Ford",
    "Maruti",
    "Renault",
    "Volkswagen",
    "Skoda",
    "Mahindra",
    "Tata",
]

DEFAULT_VALUES = {
    "seller_type": "Dealer",
    "fuel_type": "Petrol",
    "transmission_type": "Manual",
    "mileage": 18.0,
    "engine": 1200.0,
    "max_power": 82.0,
    "seats": 5,
}


@dataclass
class ExtractedPriceCheck:
    request: UsedCarPricePredictionRequest | None
    missing_fields: list[str]
    asking_price_usd: float | None = None


def _extract_year(text: str) -> int | None:
    match = re.search(r"\b(20[0-2][0-9]|19[8-9][0-9])\b", text)
    if not match:
        return None
    return int(match.group(1))


def _extract_km_driven(text: str) -> int | None:
    text_lower = text.lower()

    patterns = [
        r"(\d{1,3}(?:,\d{3})+|\d+)\s*(?:km|kms|kilometers)",
        r"(\d{1,3}(?:,\d{3})+|\d+)\s*(?:mileage)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            return int(match.group(1).replace(",", ""))

    return None


def _extract_asking_price(text: str) -> float | None:
    text_lower = text.lower()

    patterns = [
        r"\$(\d{1,3}(?:,\d{3})+|\d+)",
        r"(\d{1,3}(?:,\d{3})+|\d+)\s*(?:usd|dollars)",
    ]

    for pattern in patterns:
        match = re.search(pattern, text_lower)
        if match:
            return float(match.group(1).replace(",", ""))

    return None


def _extract_brand(text: str) -> str | None:
    text_lower = text.lower()

    for brand in KNOWN_BRANDS:
        if brand.lower() in text_lower:
            if brand == "Mercedes":
                return "Mercedes-Benz"
            return brand

    return None


def _extract_model(text: str, brand: str | None) -> str | None:
    if not brand:
        return None

    text_clean = re.sub(r"[^a-zA-Z0-9\s-]", " ", text)
    words = text_clean.split()

    for index, word in enumerate(words):
        if word.lower() == brand.lower().split("-")[0].lower():
            if index + 1 < len(words):
                candidate = words[index + 1]
                if not candidate.isdigit():
                    return candidate

    return None


def _extract_fuel_type(text: str) -> str:
    text_lower = text.lower()

    if "diesel" in text_lower:
        return "Diesel"
    if "hybrid" in text_lower:
        return "Hybrid"
    if "electric" in text_lower or "ev" in text_lower:
        return "Electric"
    if "petrol" in text_lower or "gasoline" in text_lower:
        return "Petrol"

    return DEFAULT_VALUES["fuel_type"]


def _extract_transmission_type(text: str) -> str:
    text_lower = text.lower()

    if "automatic" in text_lower or "auto" in text_lower:
        return "Automatic"
    if "manual" in text_lower:
        return "Manual"

    return DEFAULT_VALUES["transmission_type"]


def extract_price_check_request(message: str) -> ExtractedPriceCheck:
    current_year = 2026

    year = _extract_year(message)
    brand = _extract_brand(message)
    model = _extract_model(message, brand)
    km_driven = _extract_km_driven(message)
    asking_price_usd = _extract_asking_price(message)

    missing_fields = []

    if brand is None:
        missing_fields.append("brand")
    if model is None:
        missing_fields.append("model")
    if year is None:
        missing_fields.append("year")
    if km_driven is None:
        missing_fields.append("km_driven")

    if missing_fields:
        return ExtractedPriceCheck(
            request=None,
            missing_fields=missing_fields,
            asking_price_usd=asking_price_usd,
        )

    vehicle_age = max(0, current_year - year)

    request = UsedCarPricePredictionRequest(
        brand=brand,
        model=model,
        vehicle_age=vehicle_age,
        km_driven=km_driven,
        seller_type=DEFAULT_VALUES["seller_type"],
        fuel_type=_extract_fuel_type(message),
        transmission_type=_extract_transmission_type(message),
        mileage=DEFAULT_VALUES["mileage"],
        engine=DEFAULT_VALUES["engine"],
        max_power=DEFAULT_VALUES["max_power"],
        seats=DEFAULT_VALUES["seats"],
    )

    return ExtractedPriceCheck(
        request=request,
        missing_fields=[],
        asking_price_usd=asking_price_usd,
    )