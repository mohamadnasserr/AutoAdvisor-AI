from backend.app.services.intent_service import (
    classify_intent,
    classify_intent_with_confidence,
    rule_based_intent,
)


def test_ml_intent_classifier_routes_recommendation():
    intent = classify_intent("I need a reliable used car under 10000")

    assert intent == "car_recommendation"


def test_ml_intent_classifier_routes_comparison():
    intent = classify_intent("Compare Corolla and Civic")

    assert intent == "car_comparison"


def test_ml_intent_classifier_routes_price_check():
    intent = classify_intent("Is this car overpriced or fair value?")

    assert intent == "price_check"


def test_ml_intent_classifier_routes_image_analysis():
    intent = classify_intent("I want to upload a car photo and estimate price")

    assert intent == "image_analysis"


def test_ml_intent_classifier_routes_dealer_contact():
    intent = classify_intent("Prepare a message for the dealer")

    assert intent == "dealer_contact"


def test_ml_intent_classifier_routes_general_advice():
    intent = classify_intent("What should I check before buying a used car?")

    assert intent == "general_advice"


def test_intent_classifier_returns_confidence_or_fallback_none():
    intent, confidence = classify_intent_with_confidence("Compare Toyota Corolla and Honda Civic")

    assert intent in {
        "car_recommendation",
        "car_comparison",
        "price_check",
        "image_analysis",
        "dealer_contact",
        "general_advice",
    }

    if confidence is not None:
        assert 0.0 <= confidence <= 1.0


def test_rule_based_fallback_still_available():
    intent = rule_based_intent("connect me with the seller")

    assert intent == "dealer_contact"