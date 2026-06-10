from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.app.db.database import get_db
from backend.app.models.db_models import Car
from backend.app.models.schemas import CarResponse, CarSearchResponse


router = APIRouter(tags=["cars"])


@router.get("/cars", response_model=CarSearchResponse)
def list_cars(
    db: Session = Depends(get_db),
):
    cars = db.query(Car).order_by(Car.id.asc()).all()

    return {
        "results": cars,
        "count": len(cars),
    }


@router.get("/cars/{car_id}", response_model=CarResponse)
def get_car(
    car_id: int,
    db: Session = Depends(get_db),
):
    car = db.query(Car).filter(Car.id == car_id).first()

    if car is None:
        raise HTTPException(status_code=404, detail="Car not found")

    return car


@router.get("/search/cars", response_model=CarSearchResponse)
def search_cars(
    budget_max: float | None = Query(default=None),
    listing_type: str | None = Query(default=None),
    make: str | None = Query(default=None),
    model: str | None = Query(default=None),
    body_type: str | None = Query(default=None),
    fuel: str | None = Query(default=None),
    region: str | None = Query(default=None),
    transmission: str | None = Query(default=None),
    max_mileage_km: int | None = Query(default=None),
    availability_status: str | None = Query(default=None),
    db: Session = Depends(get_db),
):
    query = db.query(Car)

    if budget_max is not None:
        query = query.filter(Car.price_usd <= budget_max)

    if listing_type:
        query = query.filter(Car.listing_type.ilike(f"%{listing_type}%"))

    if make:
        query = query.filter(Car.make.ilike(f"%{make}%"))

    if model:
        query = query.filter(Car.model.ilike(f"%{model}%"))

    if body_type:
        query = query.filter(Car.body_type.ilike(f"%{body_type}%"))

    if fuel:
        query = query.filter(Car.fuel.ilike(f"%{fuel}%"))

    if region:
        query = query.filter(Car.region.ilike(f"%{region}%"))

    if transmission:
        query = query.filter(Car.transmission.ilike(f"%{transmission}%"))

    if max_mileage_km is not None:
        query = query.filter(Car.mileage_km <= max_mileage_km)

    if availability_status:
        query = query.filter(Car.availability_status.ilike(f"%{availability_status}%"))

    cars = query.order_by(Car.price_usd.asc()).limit(50).all()

    return {
        "results": cars,
        "count": len(cars),
    }