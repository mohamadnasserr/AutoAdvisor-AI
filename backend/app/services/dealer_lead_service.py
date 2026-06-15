from sqlalchemy.orm import Session

from backend.app.models.db_models import Car, DealerLead
from backend.app.models.schemas import DealerLeadCreateRequest, DealerLeadResponse
from backend.app.services.preference_service import extract_preferences

def build_dealer_inquiry_draft(car: Car) -> str:
    car_title = f"{car.year} {car.make} {car.model}"

    return (
        f"Hello, I am interested in the {car_title} listed on AutoAdvisor AI. "
        "Could you please confirm availability, final price, mileage, service history, "
        "accident history, and whether a pre-purchase inspection is possible? Thank you."
    )


def create_dealer_lead(
    db: Session,
    request: DealerLeadCreateRequest,
) -> DealerLeadResponse:
    car = db.query(Car).filter(Car.id == request.selected_car_id).first()

    if car is None:
        raise ValueError("Selected car not found.")

    dealership = car.dealer
    message_draft = build_dealer_inquiry_draft(car)

    lead = DealerLead(
        selected_car_id=car.id,
        customer_name=request.customer_name,
        customer_phone=request.customer_phone,
        customer_email=request.customer_email,
        notes=request.notes,
        budget=request.budget,
        user_location=request.user_location,
        preferred_contact_method=request.preferred_contact_method,
        message_draft=message_draft,
        status="draft_created",
    )

    db.add(lead)
    db.commit()
    db.refresh(lead)

    return DealerLeadResponse(
        lead_id=lead.id,
        selected_car_id=car.id,
        customer_name=lead.customer_name,
        customer_phone=lead.customer_phone,
        customer_email=lead.customer_email,
        dealership_name=dealership.name if dealership else None,
        dealership_location=dealership.location if dealership else None,
        dealership_phone=dealership.phone if dealership else None,
        dealership_email=dealership.email if dealership else None,
        message_draft=message_draft,
        status=lead.status,
    )

def find_car_for_dealer_request(db: Session, message: str) -> Car | None:
    text = message.lower()
    prefs = extract_preferences(message)

    query = db.query(Car)

    if prefs.brand_preference:
        query = query.filter(Car.make.ilike(f"%{prefs.brand_preference}%"))

    if prefs.budget_max:
        query = query.filter(Car.price_usd <= prefs.budget_max)

    cars = query.order_by(Car.id.asc()).all()

    if not cars:
        cars = db.query(Car).order_by(Car.id.asc()).all()

    for car in cars:
        make = car.make.lower()
        model = car.model.lower()
        full_name = f"{make} {model}"

        if full_name in text or model in text or make in text:
            return car

    return cars[0] if cars else None
