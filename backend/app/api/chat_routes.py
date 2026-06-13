from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.services.guardrail_service import check_text_guardrails
from backend.app.services.price_check_service import extract_price_check_request
from backend.app.services.price_estimator_service import price_estimator
from backend.app.services.chat_memory_service import ChatMemoryService
from backend.app.models.schemas import ChatRequest, ChatResponse
from backend.app.services.comparison_service import (
    build_comparison_chat_answer,
    compare_cars_by_ids,
    find_cars_for_comparison_message,
)
from backend.app.services.intent_service import classify_intent
from backend.app.services.preference_service import extract_preferences
from backend.app.services.recommendation_service import (
    build_recommendation_answer,
    recommend_cars,
)
from backend.app.models.schemas import DealerLeadCreateRequest
from backend.app.services.dealer_lead_service import (
    create_dealer_lead,
    find_car_for_dealer_request,
)

from backend.app.services.rag_service import build_rag_answer, retrieve_semantic_rag_sources

router = APIRouter(tags=["chat"])

memory_service = ChatMemoryService()

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
    guardrail_result = check_text_guardrails(request.message)

    if not guardrail_result.allowed:
        session_id = request.session_id or "default"

        memory_service.add_message(
            session_id=session_id,
            role="user",
            content=request.message,
        )

        memory_service.add_message(
            session_id=session_id,
            role="assistant",
            content=guardrail_result.safe_response or "I cannot help with that request.",
        )

        return ChatResponse(
            session_id=session_id,
            intent="guardrail_blocked",
            extracted_preferences=extract_preferences(request.message),
            answer=guardrail_result.safe_response or "I cannot help with that request.",
            recommended_cars=[],
        )
    intent = classify_intent(request.message)
    prefs = extract_preferences(request.message)
    session_id = request.session_id or "default"
    memory_service.add_message(
        session_id=session_id,
        role="user",
        content=request.message,
    )
    recommended_cars = []

    if intent == "car_recommendation":
        if prefs.listing_type is None:
            answer = build_listing_type_clarification(prefs.budget_max)
        else:
            recommended_cars = recommend_cars(db=db, prefs=prefs)
            answer = build_recommendation_answer(recommended_cars, prefs)

    elif intent == "price_check":

        extracted_price_check = extract_price_check_request(request.message)

        if extracted_price_check.request is None:
            missing = ", ".join(extracted_price_check.missing_fields)
            answer = (
                "I can estimate the fair used-car price, but I need a few details first. "
                f"Missing fields: {missing}. "
                "Please send something like: "
                "'2018 Hyundai i20, 60000 km, petrol, manual, asking $8500'."
            )
        elif not price_estimator.is_available():
            answer = "The used-car price estimator model is currently unavailable."
        else:
            prediction = price_estimator.predict(extracted_price_check.request)

            asking_price = extracted_price_check.asking_price_usd
            if asking_price is None:
                asking_price_text = "You did not provide an asking price, so I can only provide a fair range."
                verdict = "Compare the seller's asking price against this range before negotiating."
            elif asking_price < prediction.low_estimate_usd:
                asking_price_text = f"Asking price: ${asking_price:,.0f}."
                verdict = "This looks below the estimated fair range. Verify condition, accident history, papers, and hidden issues."
            elif asking_price > prediction.high_estimate_usd:
                asking_price_text = f"Asking price: ${asking_price:,.0f}."
                verdict = "This looks overpriced versus the estimated fair range. Negotiate or compare with similar listings."
            else:
                asking_price_text = f"Asking price: ${asking_price:,.0f}."
                verdict = "This asking price falls inside the estimated fair range."

            answer = (
                "Used-car fair price estimate:\n"
                f"- Estimated price: ${prediction.estimated_price_usd:,.0f}\n"
                f"- Fair range: ${prediction.low_estimate_usd:,.0f}–${prediction.high_estimate_usd:,.0f}\n"
                f"- {asking_price_text}\n"
                f"- Verdict: {verdict}\n\n"
                f"Model info: MAE ≈ ${prediction.model_mae_usd:,.0f}, R² ≈ {prediction.model_r2}.\n"
                f"Note: {prediction.disclaimer}"
            )

    elif intent == "general_advice":
        rag_sources = retrieve_semantic_rag_sources(db, request.message, limit=3)
        answer = build_rag_answer(request.message, rag_sources)

    elif intent == "car_comparison":
        cars_to_compare = find_cars_for_comparison_message(
            db=db,
            message=request.message,
        )

        if len(cars_to_compare) < 2:
            answer = (
                "I need at least 2 cars to compare. "
                "Please mention 2 to 5 models, for example: "
                "Compare Toyota Corolla, Honda Civic, and Hyundai Elantra."
            )
        else:
            car_ids = [car.id for car in cars_to_compare[:5]]
            comparison_items, final_verdict, _ = compare_cars_by_ids(
                db=db,
                car_ids=car_ids,
            )
            answer = build_comparison_chat_answer(
                comparison_items=comparison_items,
                final_verdict=final_verdict,
            )
            recommended_cars = cars_to_compare[:5]

    elif intent == "dealer_contact":

        selected_car = find_car_for_dealer_request(db, request.message)

        if selected_car is None:
            answer = (
                "I can prepare a dealer inquiry, but I could not find a matching car in the current inventory. "
                "Please mention the make/model, for example: 'Connect me with the dealer for the Toyota Corolla'."
            )
        else:
            lead_request = DealerLeadCreateRequest(
                selected_car_id=selected_car.id,
                user_location=prefs.region,
                preferred_contact_method="phone",
                budget=prefs.budget_max,
            )

        lead = create_dealer_lead(db, lead_request)

        dealer_line = (
            f"{lead.dealership_name} in {lead.dealership_location}"
            if lead.dealership_name and lead.dealership_location
            else "the matched dealership"
        )

        answer = (
            f"I created a draft dealer inquiry for the {selected_car.year} {selected_car.make} {selected_car.model}.\n\n"
            f"Matched dealer: {dealer_line}\n"
            f"Lead status: {lead.status}\n\n"
            f"Inquiry draft:\n{lead.message_draft}\n\n"
            "Note: I did not send this message automatically. This is a draft lead for demo/safety purposes."
        )

    elif intent == "image_analysis":
        answer = (
            "Image-assisted price estimation is coming next. The image workflow will run safety checks, "
            "quality checks, vehicle detection, color/body-type detection, optional make/model suggestion, "
            "then ask the user to confirm structured fields before predicting a used-car price range."
        )

    else:
        answer = "I can help with car recommendations, comparisons, price checks, image analysis, and dealer inquiries."

    memory_service.add_message(

        session_id=session_id,
        role="assistant",
        content=answer,
    )

    return ChatResponse(
    session_id=session_id,
    intent=intent,
    extracted_preferences=prefs,
    answer=answer,
    recommended_cars=recommended_cars,
    )