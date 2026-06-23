from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.models.db_models import DealerUser
from backend.app.models.schemas import (
    DealerLeadListItem,
    DealerLoginRequest,
    DealerLoginResponse,
    DealerUserProfile,
)
from backend.app.services.dealer_auth_service import (
    authenticate_dealer_user,
    build_dealer_profile,
    create_access_token,
    get_current_dealer_user,
)
from backend.app.services.dealer_lead_service import list_dealer_leads


router = APIRouter(prefix="/dealer", tags=["dealer-auth"])


@router.post("/auth/login", response_model=DealerLoginResponse)
def dealer_login(
    request: DealerLoginRequest,
    db: Session = Depends(get_db),
) -> DealerLoginResponse:
    dealer_user = authenticate_dealer_user(db, request.email, request.password)
    if dealer_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid dealer email or password.",
        )

    return DealerLoginResponse(
        access_token=create_access_token(dealer_user),
        dealer_user=build_dealer_profile(dealer_user),
    )


@router.get("/auth/me", response_model=DealerUserProfile)
def dealer_me(
    dealer_user: DealerUser = Depends(get_current_dealer_user),
) -> DealerUserProfile:
    return build_dealer_profile(dealer_user)


@router.get("/me/leads", response_model=list[DealerLeadListItem])
def dealer_my_leads(
    status: str | None = None,
    dealer_user: DealerUser = Depends(get_current_dealer_user),
    db: Session = Depends(get_db),
) -> list[DealerLeadListItem]:
    return list_dealer_leads(
        db=db,
        dealer_id=dealer_user.dealership_id,
        lead_status=status,
    )
