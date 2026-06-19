from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.models.schemas import (
    UsedCarPricePredictionRequest,
    UsedCarPricePredictionResponse,
)
from backend.app.services.price_estimator_service import price_estimator


router = APIRouter(tags=["price-estimator"])


@router.post("/price/used-car", response_model=UsedCarPricePredictionResponse)
def predict_used_car_price(
    request: UsedCarPricePredictionRequest,
    db: Session = Depends(get_db),
) -> UsedCarPricePredictionResponse:
    if not price_estimator.is_available():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Used-car price estimator model is not available.",
        )

    return price_estimator.predict(request, db=db)
