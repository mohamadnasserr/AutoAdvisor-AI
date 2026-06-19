from pathlib import Path
import re

import joblib

from backend.app.config import settings


MODEL_PATH = Path(settings.model_dir) / "intent_classifier.joblib"

VALID_INTENTS = {
    "car_recommendation",
    "car_comparison",
    "price_check",
    "image_analysis",
    "dealer_contact",
    "general_advice",
    "greeting",
}

GREETING_MESSAGES = {
    "hello",
    "hi",
    "hey",
    "hello there",
    "hi there",
    "good morning",
    "good afternoon",
    "good evening",
    "how are you",
}

GENERAL_ADVICE_PATTERNS = [
    "what should i check",
    "how do i",
    "how can i",
    "what documents",
    "what papers",
    "buying tips",
    "inspection",
    "inspect a used car",
    "maintenance",
    "depreciation",
    "accident history",
    "service history",
    "red flags",
    "mileage tampering",
    "new or used smarter",
    "should i buy new or used",
]

RECOMMENDATION_ACTION_PATTERNS = [
    "recommend",
    "find me",
    "show me",
    "suggest",
    "looking for",
    "i need",
    "i want",
    "help me pick",
    "what car should i get",
]

VEHICLE_SHOPPING_TERMS = [
    "car",
    "vehicle",
    "auto",
    "sedan",
    "suv",
    "hatchback",
    "coupe",
    "pickup",
    "van",
    "fast",
    "sport",
    "sporty",
    "performance",
    "luxury",
    "premium",
    "exotic",
    "supercar",
    "ferrari",
    "lamborghini",
    "porsche",
    "amg",
    "gtr",
    "gt-r",
    "corvette",
]

SHOPPING_DETAIL_PATTERNS = [
    "used car",
    "new car",
    "brand new",
    "family car",
    "city car",
    "reliable",
    "cheap",
    "affordable",
    "budget",
    "beirut",
    "lebanon",
    "tripoli",
    "saida",
    "jounieh",
    "above one million",
    "over one million",
    "more than one million",
    "extravagant",
]

BUDGET_PATTERN = (
    r"(?:under|below|around|max(?:imum)?|budget|for|between|from|more than|"
    r"above|over|greater than|starting|minimum|not less than)\s*\$?\s*[\d,]+"
)


def deterministic_intent_override(message: str) -> str | None:
    text = " ".join(message.lower().strip().split())

    if text in GREETING_MESSAGES:
        return "greeting"

    if any(pattern in text for pattern in ["compare", " vs ", "versus", "difference between", "which is better"]):
        return "car_comparison"

    if any(word in text for word in ["dealer", "dealership", "connect", "contact", "call", "message", "seller"]):
        return "dealer_contact"

    if any(word in text for word in ["image", "photo", "picture", "upload", "analyze this car", "car image"]):
        return "image_analysis"

    if any(pattern in text for pattern in GENERAL_ADVICE_PATTERNS):
        return None

    has_vehicle_term = any(term in text for term in VEHICLE_SHOPPING_TERMS)
    has_action = any(pattern in text for pattern in RECOMMENDATION_ACTION_PATTERNS)
    has_budget = bool(
        re.search(BUDGET_PATTERN, text)
        or re.search(r"\$\s*[\d,]+", text)
    )
    shopping_detail_count = sum(
        pattern in text for pattern in SHOPPING_DETAIL_PATTERNS
    )

    if has_vehicle_term and (has_action or has_budget or shopping_detail_count >= 1):
        return "car_recommendation"

    if any(word in text for word in ["price", "fair", "overpriced", "worth", "value", "estimate"]):
        return "price_check"

    return None


def rule_based_intent(message: str) -> str:
    text = message.lower()

    override = deterministic_intent_override(message)
    if override is not None:
        return override

    if any(word in text for word in ["compare", "vs", "versus", "difference between", "which is better"]):
        return "car_comparison"

    if any(word in text for word in ["dealer", "dealership", "connect", "contact", "call", "message", "seller"]):
        return "dealer_contact"

    if any(word in text for word in ["image", "photo", "picture", "upload", "analyze this car", "car image"]):
        return "image_analysis"

    if any(word in text for word in ["price", "fair", "overpriced", "worth", "value", "estimate"]):
        return "price_check"

    if any(word in text for word in ["recommend", "need", "want", "looking for", "budget", "family", "city"]):
        return "car_recommendation"

    return "general_advice"


class IntentClassifier:
    def __init__(self) -> None:
        self.model = None

        if MODEL_PATH.exists():
            try:
                self.model = joblib.load(MODEL_PATH)
            except Exception:
                self.model = None

    def predict(self, message: str) -> tuple[str, float | None]:
        override = deterministic_intent_override(message)
        if override is not None:
            return override, 1.0

        if self.model is None:
            return rule_based_intent(message), None

        try:
            prediction = self.model.predict([message])[0]

            confidence = None
            if hasattr(self.model, "predict_proba"):
                probabilities = self.model.predict_proba([message])[0]
                confidence = float(max(probabilities))

            if prediction not in VALID_INTENTS:
                return rule_based_intent(message), confidence

            if confidence is not None and confidence < 0.35:
                return rule_based_intent(message), confidence

            return str(prediction), confidence

        except Exception:
            return rule_based_intent(message), None


_classifier = IntentClassifier()


def classify_intent(message: str) -> str:
    intent, _ = _classifier.predict(message)
    return intent


def classify_intent_with_confidence(message: str) -> tuple[str, float | None]:
    return _classifier.predict(message)
