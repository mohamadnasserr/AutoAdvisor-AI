from pathlib import Path

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
}


def rule_based_intent(message: str) -> str:
    text = message.lower()

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