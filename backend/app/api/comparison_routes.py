from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.models.schemas import CompareCarsRequest, CompareCarsResponse
from backend.app.services.comparison_service import compare_cars_by_ids


router = APIRouter(tags=["comparison"])


@router.post("/compare", response_model=CompareCarsResponse)
def compare_cars(
    request: CompareCarsRequest,
    db: Session = Depends(get_db),
):
    try:
        comparison_items, final_verdict, best_car_id = compare_cars_by_ids(
            db=db,
            car_ids=request.car_ids,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc

    return CompareCarsResponse(
        compared_count=len(comparison_items),
        cars=comparison_items,
        best_overall_car_id=best_car_id,
        final_verdict=final_verdict,
    )