import re

from backend.app.models.schemas import PreferenceExtraction


BODY_TYPES = ["sedan", "suv", "hatchback", "coupe", "pickup", "van"]
FUEL_TYPES = ["petrol", "diesel", "hybrid", "electric"]
TRANSMISSIONS = ["automatic", "manual"]

BRAND_ALIASES = {
    "toyota": "Toyota",
    "honda": "Honda",
    "kia": "Kia",
    "hyundai": "Hyundai",
    "nissan": "Nissan",
    "bmw": "BMW",
    "mercedes-benz": "Mercedes-Benz",
    "mercedes": "Mercedes-Benz",
    "audi": "Audi",
    "lexus": "Lexus",
    "ferrari": "Ferrari",
    "lamborghini": "Lamborghini",
    "porsche": "Porsche",
    "bentley": "Bentley",
    "rolls-royce": "Rolls-Royce",
    "rolls royce": "Rolls-Royce",
    "range rover": "Land Rover",
    "land rover": "Land Rover",
    "chevrolet": "Chevrolet",
    "ford": "Ford",
    "jeep": "Jeep",
}

BRANDS = sorted(BRAND_ALIASES, key=len, reverse=True)

PERFORMANCE_TERMS = [
    "fast",
    "sport",
    "sporty",
    "performance",
    "sports car",
    "amg",
    "competition",
    "rs7",
    "gt-r",
    "gtr",
    "corvette",
    "turbo s",
    "gt3",
]

LUXURY_TERMS = [
    "luxury",
    "premium",
    "fancy",
    "extravagant",
    "maybach",
    "bentley",
    "rolls",
    "range rover",
    "s-class",
    "g63",
    "lexus",
]

EXOTIC_TERMS = [
    "exotic",
    "supercar",
    "ferrari",
    "lamborghini",
    "huracan",
    "aventador",
    "sf90",
    "f8",
    "488",
    "above one million",
    "over one million",
    "more than one million",
]


def _money_value(raw_value: str) -> float:
    normalized = raw_value.lower().replace("$", "").replace(",", "").strip()
    multiplier = 1000 if normalized.endswith("k") else 1
    normalized = normalized.removesuffix("k").strip()
    return float(normalized) * multiplier


def extract_budget_range(text: str) -> tuple[float | None, float | None]:
    cleaned = text.lower().replace(",", "")
    money = r"\$?\s*\d+(?:\.\d+)?\s*k?"

    range_patterns = [
        rf"between\s+({money})\s+(?:and|to|-)\s+({money})",
        rf"from\s+({money})\s+(?:to|-)\s+({money})",
        rf"({money})\s*(?:-|to)\s*({money})",
    ]

    for pattern in range_patterns:
        match = re.search(pattern, cleaned)
        if match:
            first = _money_value(match.group(1))
            second = _money_value(match.group(2))
            return min(first, second), max(first, second)

    return None, None


def extract_budget_minimum(text: str) -> float | None:
    cleaned = text.lower().replace(",", "")
    money = r"\$?\s*\d+(?:\.\d+)?\s*k?"

    if re.search(r"(?:more than|above|over|greater than)\s+one million", cleaned):
        return 1_000_000

    minimum_patterns = [
        rf"more than\s+({money})",
        rf"above\s+({money})",
        rf"over\s+({money})",
        rf"greater than\s+({money})",
        rf"from\s+({money})",
        rf"starting\s+({money})",
        rf"minimum\s+({money})",
        rf"not less than\s+({money})",
    ]

    for pattern in minimum_patterns:
        match = re.search(pattern, cleaned)
        if match:
            return _money_value(match.group(1))

    return None


def extract_budget(text: str) -> float | None:
    cleaned = text.lower().replace(",", "")
    _, budget_max = extract_budget_range(cleaned)

    if budget_max is not None:
        return budget_max

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

    budget_min, budget_max = extract_budget_range(text)
    budget_min = budget_min or extract_budget_minimum(text)
    budget = budget_max if budget_max is not None else (
        None if budget_min is not None else extract_budget(text)
    )
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

    performance_intent = any(term in text for term in PERFORMANCE_TERMS)
    luxury_preference = any(
        word in text for word in ["luxury", "fancy", "premium", "bmw", "mercedes"]
    ) or any(term in text for term in LUXURY_TERMS)
    exotic_intent = any(term in text for term in EXOTIC_TERMS)

    if brand in {"ferrari", "lamborghini", "porsche"}:
        performance_intent = True

    if brand in {"ferrari", "lamborghini", "bentley", "rolls-royce", "rolls royce"}:
        exotic_intent = True

    if brand in {"bmw", "mercedes", "mercedes-benz", "audi", "lexus", "bentley", "rolls-royce", "rolls royce", "range rover", "land rover"}:
        luxury_preference = True

    if budget_min is not None and budget_min >= 1_000_000:
        exotic_intent = True
        luxury_preference = True

    style_preference = None
    if exotic_intent:
        style_preference = "exotic"
    elif performance_intent:
        style_preference = "performance"
    elif luxury_preference:
        style_preference = "luxury"

    if style_preference and listing_type is None:
        listing_type = "both"

    if luxury_preference:
        priorities.append("premium comfort")

    if performance_intent:
        priorities.append("performance")

    if exotic_intent:
        priorities.append("exotic appeal")

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
        budget_min=budget_min,
        region=region,
        listing_type=listing_type,
        use_case=use_case,
        body_type=body_type.title() if body_type else None,
        fuel=fuel.title() if fuel else None,
        transmission=transmission.title() if transmission else None,
        brand_preference=BRAND_ALIASES[brand] if brand else None,
        luxury_preference=luxury_preference,
        performance_intent=performance_intent,
        exotic_intent=exotic_intent,
        style_preference=style_preference,
        priorities=list(dict.fromkeys(priorities)),
    )
