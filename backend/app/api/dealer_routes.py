from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.models.schemas import DealerLeadCreateRequest, DealerLeadResponse
from backend.app.services.dealer_lead_service import create_dealer_lead


router = APIRouter(tags=["dealer-leads"])


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