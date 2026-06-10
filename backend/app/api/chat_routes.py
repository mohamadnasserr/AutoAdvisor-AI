from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.models.schemas import ChatRequest, ChatResponse
from backend.app.services.intent_service import classify_intent
from backend.app.services.preference_service import extract_preferences
from backend.app.services.recommendation_service import (
    build_recommendation_answer,
    recommend_cars,
)


router = APIRouter(tags=["chat"])


def build_listing_type_clarification(budget_max: float | None) -> str:
    if budget_max is not None and budget_max <= 12000:
        return (
            "Do you prefer a used car, a new car, or are you open to both? "
            f"With a budget around ${budget_max:,.0f}, used cars are usually the more realistic option, "
            "but I can still compare both if you want."
        )

    return (
        "Do you prefer a used car, a new car, or are you open to both? "
        "This choice changes the recommendation because used cars are judged by mileage and condition, "
        "while new cars are judged more by warranty, trim, and reference price."
    )


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    intent = classify_intent(request.message)
    prefs = extract_preferences(request.message)

    recommended_cars = []

    if intent == "car_recommendation":
        if prefs.listing_type is None:
            answer = build_listing_type_clarification(prefs.budget_max)
        else:
            recommended_cars = recommend_cars(db=db, prefs=prefs)
            answer = build_recommendation_answer(recommended_cars, prefs)

    elif intent == "price_check":
        if prefs.listing_type is None:
            answer = build_listing_type_clarification(prefs.budget_max)
        else:
            recommended_cars = recommend_cars(db=db, prefs=prefs)
            answer = build_recommendation_answer(recommended_cars, prefs)

    elif intent == "general_advice":
        answer = (
            "I can help with car recommendations, used-vs-new tradeoffs, comparisons, "
            "price checks, image-assisted price estimation, and dealer inquiry drafts. "
            "Tell me your budget, preferred listing type, and main use case."
        )

    elif intent == "car_comparison":
        answer = (
            "Comparison workflow is coming next. For the MVP, I will compare cars using "
            "price, mileage, reliability, maintenance risk, warranty, and RAG-backed buying advice."
        )

    elif intent == "dealer_contact":
        answer = (
            "Dealer connection workflow is coming next. The MVP will generate an inquiry draft "
            "and store it only after user confirmation."
        )

    elif intent == "image_analysis":
        answer = (
            "Image-assisted price estimation is coming next. The image workflow will run safety checks, "
            "quality checks, vehicle detection, color/body-type detection, optional make/model suggestion, "
            "then ask the user to confirm structured fields before predicting a used-car price range."
        )

    else:
        answer = "I can help with car recommendations, comparisons, price checks, image analysis, and dealer inquiries."

    return ChatResponse(
        intent=intent,
        extracted_preferences=prefs,
        answer=answer,
        recommended_cars=recommended_cars,
    )