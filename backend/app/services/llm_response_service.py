from typing import Any

from openai import OpenAI

from backend.app.config import settings


SYSTEM_PROMPT = (
    "You are AutoAdvisor AI, a Lebanon/MENA car-buying assistant. Rewrite "
    "backend-generated draft answers into natural, helpful chatbot replies. "
    "Keep the facts unchanged. Do not invent cars, prices, dealerships, or "
    "live availability. Do not expose JSON or internal tool details. Be "
    "concise, practical, and friendly. Do not guarantee availability, prices, "
    "legal outcomes, financing, insurance, or dealer response. If the intent "
    "is dealer_contact, clearly state that the inquiry is a draft and was not "
    "sent automatically. Preserve clear clarification questions."
)


def _preference_summary(extracted_preferences: Any) -> str:
    if hasattr(extracted_preferences, "model_dump"):
        values = extracted_preferences.model_dump()
    elif isinstance(extracted_preferences, dict):
        values = extracted_preferences
    else:
        return "No structured preferences available."

    meaningful_values = [
        f"{key}: {value}"
        for key, value in values.items()
        if value not in (None, "", [], False)
    ]
    return "; ".join(meaningful_values) or "No structured preferences available."


def _car_summary(car: Any) -> str:
    fields = (
        "id",
        "year",
        "make",
        "model",
        "listing_type",
        "price_usd",
        "mileage_km",
        "body_type",
        "fuel",
        "transmission",
        "region",
        "availability_status",
    )

    if hasattr(car, "model_dump"):
        values = car.model_dump()
    elif isinstance(car, dict):
        values = car
    else:
        values = {field: getattr(car, field, None) for field in fields}

    return ", ".join(
        f"{field}={values.get(field)}"
        for field in fields
        if values.get(field) is not None
    )


def rewrite_chat_answer_with_llm(
    *,
    user_message: str,
    intent: str,
    draft_answer: str,
    extracted_preferences: Any,
    recommended_cars: list[Any],
) -> str:
    if settings.llm_provider.lower() != "openai" or not settings.openai_api_key:
        return draft_answer.strip()

    car_summaries = "\n".join(
        f"- {_car_summary(car)}" for car in recommended_cars
    ) or "No recommended cars were returned."

    rewrite_input = (
        f"User message:\n{user_message}\n\n"
        f"Intent:\n{intent}\n\n"
        f"Extracted preferences:\n{_preference_summary(extracted_preferences)}\n\n"
        f"Recommended inventory cars:\n{car_summaries}\n\n"
        f"Backend draft answer:\n{draft_answer}\n\n"
        "Rewrite only the final user-facing answer. Return plain natural text, "
        "not JSON."
    )

    try:
        client = OpenAI(
            api_key=settings.openai_api_key,
            timeout=20.0,
            max_retries=1,
        )
        response = client.responses.create(
            model=settings.openai_model,
            instructions=SYSTEM_PROMPT,
            input=rewrite_input,
        )
        final_answer = response.output_text.strip()
        return final_answer or draft_answer.strip()
    except Exception:
        return draft_answer.strip()
