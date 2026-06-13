from sqlalchemy.orm import Session

from backend.app.models.db_models import Car, DealerLead
from backend.app.models.schemas import DealerLeadCreateRequest, DealerLeadResponse


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
        dealership_name=dealership.name if dealership else None,
        dealership_location=dealership.location if dealership else None,
        dealership_phone=dealership.phone if dealership else None,
        dealership_email=dealership.email if dealership else None,
        message_draft=message_draft,
        status=lead.status,
    )