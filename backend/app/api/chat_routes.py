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


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    intent = classify_intent(request.message)
    prefs = extract_preferences(request.message)

    recommended_cars = []

    if intent in ["car_recommendation", "price_check", "general_advice"]:
        recommended_cars = recommend_cars(db=db, prefs=prefs)
        answer = build_recommendation_answer(recommended_cars, prefs)

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