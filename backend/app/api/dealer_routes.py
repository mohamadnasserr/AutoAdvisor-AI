from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.models.schemas import (
    DealerLeadCreateRequest,
    DealerLeadListItem,
    DealerLeadResponse,
    DealershipListItem,
)
from backend.app.services.dealer_lead_service import (
    create_dealer_lead,
    list_dealer_leads,
    list_dealerships,
)


router = APIRouter(tags=["dealer-leads"])


@router.get("/dealer/dealerships", response_model=list[DealershipListItem])
def get_dealerships(
    db: Session = Depends(get_db),
) -> list[DealershipListItem]:
    return list_dealerships(db)


@router.get("/dealer/leads", response_model=list[DealerLeadListItem])
def get_leads(
    dealer_id: int | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
) -> list[DealerLeadListItem]:
    return list_dealer_leads(
        db=db,
        dealer_id=dealer_id,
        lead_status=status,
    )


@router.post("/dealer/leads", response_model=DealerLeadResponse)
def create_lead(
    request: DealerLeadCreateRequest,
    db: Session = Depends(get_db),
) -> DealerLeadResponse:
    try:
        return create_dealer_lead(db, request)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
