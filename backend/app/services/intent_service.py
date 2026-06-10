def classify_intent(message: str) -> str:
    text = message.lower()

    if any(word in text for word in ["compare", "vs", "versus", "difference between"]):
        return "car_comparison"

    if any(word in text for word in ["dealer", "dealership", "connect", "contact", "call", "message"]):
        return "dealer_contact"

    if any(word in text for word in ["image", "photo", "picture", "upload", "analyze this car"]):
        return "image_analysis"

    if any(word in text for word in ["price", "fair", "overpriced", "worth"]):
        return "price_check"

    if any(word in text for word in ["recommend", "need", "want", "looking for", "budget", "family", "city"]):
        return "car_recommendation"

    return "general_advice"