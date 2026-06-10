import re

from backend.app.models.schemas import PreferenceExtraction


BODY_TYPES = ["sedan", "suv", "hatchback", "coupe", "pickup", "van"]
FUEL_TYPES = ["petrol", "diesel", "hybrid", "electric"]
TRANSMISSIONS = ["automatic", "manual"]

BRANDS = [
    "toyota",
    "honda",
    "kia",
    "hyundai",
    "nissan",
    "bmw",
    "mercedes",
    "mercedes-benz",
]


def extract_budget(text: str) -> float | None:
    cleaned = text.lower().replace(",", "")

    patterns = [
        r"under\s*\$?(\d+)",
        r"below\s*\$?(\d+)",
        r"budget\s*(?:around|of)?\s*\$?(\d+)",
        r"\$?(\d+)\s*(?:budget|max|maximum)",
        r"around\s*\$?(\d+)",
        r"for\s*\$?(\d+)",
        r"\$?(\d+)",
    ]

    for pattern in patterns:
        match = re.search(pattern, cleaned)
        if match:
            return float(match.group(1))

    return None


def extract_listing_type(text: str) -> str | None:
    lowered = text.lower()

    both_patterns = [
        "new or used",
        "used or new",
        "new and used",
        "used and new",
        "open to new or used",
        "open to used or new",
        "either new or used",
        "either used or new",
    ]

    if any(pattern in lowered for pattern in both_patterns):
        return "both"

    new_patterns = [
        "new car",
        "brand new",
        "zero mileage",
        "0 mileage",
        "new vehicle",
    ]

    if any(pattern in lowered for pattern in new_patterns):
        return "new"

    used_patterns = [
        "used",
        "second hand",
        "second-hand",
        "pre owned",
        "pre-owned",
    ]

    if any(pattern in lowered for pattern in used_patterns):
        return "used"

    return None

def extract_preferences(message: str) -> PreferenceExtraction:
    text = message.lower()

    budget = extract_budget(text)
    listing_type = extract_listing_type(text)

    body_type = next((b for b in BODY_TYPES if b in text), None)
    fuel = next((f for f in FUEL_TYPES if f in text), None)
    transmission = next((t for t in TRANSMISSIONS if t in text), None)
    brand = next((b for b in BRANDS if b in text), None)

    use_case = None
    priorities: list[str] = []

    if "city" in text or "parking" in text or "traffic" in text:
        use_case = "city"
        priorities.extend(["fuel economy", "easy parking", "low maintenance"])

    if "family" in text or "kids" in text:
        use_case = "family"
        priorities.extend(["space", "safety", "comfort"])

    luxury_preference = any(
        word in text for word in ["luxury", "fancy", "premium", "bmw", "mercedes"]
    )

    if luxury_preference:
        priorities.append("premium comfort")

    if "reliable" in text or "reliability" in text:
        priorities.append("reliability")

    if "cheap maintenance" in text or "low maintenance" in text or "not expensive to maintain" in text:
        priorities.append("low maintenance")

    region = "Lebanon"
    for possible_region in ["beirut", "jounieh", "zahle", "tripoli", "saida", "lebanon"]:
        if possible_region in text:
            region = possible_region.title()

    return PreferenceExtraction(
        budget_max=budget,
        region=region,
        listing_type=listing_type,
        use_case=use_case,
        body_type=body_type.title() if body_type else None,
        fuel=fuel.title() if fuel else None,
        transmission=transmission.title() if transmission else None,
        brand_preference=brand.title() if brand else None,
        luxury_preference=luxury_preference,
        priorities=list(dict.fromkeys(priorities)),
    )