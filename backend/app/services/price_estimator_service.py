from pathlib import Path
from statistics import median

import joblib
import pandas as pd
from sqlalchemy.orm import Session

from backend.app.config import settings
from backend.app.models.db_models import Car
from backend.app.models.schemas import (
    UsedCarPricePredictionRequest,
    UsedCarPricePredictionResponse,
)


MODEL_PATH = Path(settings.model_dir) / "used_car_price_estimator.joblib"

class UsedCarPriceEstimator:
    def __init__(self) -> None:
        self.artifact = None
        self.model = None
        self.features: list[str] = []
        self.mae_usd: float | None = None
        self.r2: float | None = None

        if MODEL_PATH.exists():
            try:
                self.artifact = joblib.load(MODEL_PATH)
                self.model = self.artifact["model"]
                self.features = self.artifact["features"]
                self.mae_usd = self.artifact.get("mae_usd")
                self.r2 = self.artifact.get("r2")
            except Exception:
                self.artifact = None
                self.model = None

    def is_available(self) -> bool:
        return self.model is not None

    def _inventory_matches(self, db: Session, request: UsedCarPricePredictionRequest) -> list[Car]:
        query = db.query(Car).filter(Car.listing_type == "used")

        available_query = query.filter(Car.availability_status == "available")

        filters = []
        if request.brand:
            filters.append(Car.make.ilike(f"%{request.brand}%"))
        if request.model:
            filters.append(Car.model.ilike(f"%{request.model}%"))
        if request.fuel_type:
            filters.append(Car.fuel.ilike(f"%{request.fuel_type}%"))
        if request.transmission_type:
            filters.append(Car.transmission.ilike(f"%{request.transmission_type}%"))

        for criterion in filters:
            available_query = available_query.filter(criterion)
            query = query.filter(criterion)

        current_year = 2026
        target_year = current_year - request.vehicle_age
        year_min = target_year - 3
        year_max = target_year + 3
        mileage_min = max(0, request.km_driven - 50000)
        mileage_max = request.km_driven + 50000

        available_query = available_query.filter(Car.year.between(year_min, year_max))
        query = query.filter(Car.year.between(year_min, year_max))

        if request.km_driven:
            available_query = available_query.filter(
                (Car.mileage_km.is_(None)) | Car.mileage_km.between(mileage_min, mileage_max)
            )
            query = query.filter(
                (Car.mileage_km.is_(None)) | Car.mileage_km.between(mileage_min, mileage_max)
            )

        matches = available_query.order_by(Car.price_usd.asc()).limit(10).all()
        if len(matches) >= 3:
            return matches

        relaxed_query = db.query(Car).filter(Car.listing_type == "used")
        if request.brand:
            relaxed_query = relaxed_query.filter(Car.make.ilike(f"%{request.brand}%"))
        if request.fuel_type:
            relaxed_query = relaxed_query.filter(Car.fuel.ilike(f"%{request.fuel_type}%"))
        if request.transmission_type:
            relaxed_query = relaxed_query.filter(Car.transmission.ilike(f"%{request.transmission_type}%"))

        relaxed_query = relaxed_query.filter(Car.year.between(target_year - 5, target_year + 5))
        relaxed_matches = relaxed_query.order_by(Car.price_usd.asc()).limit(10).all()
        return matches if len(matches) >= len(relaxed_matches) else relaxed_matches

    def _inventory_reference(self, db: Session | None, request: UsedCarPricePredictionRequest) -> tuple[float | None, float | None, float | None, int]:
        if db is None:
            return None, None, None, 0

        matches = self._inventory_matches(db, request)
        prices = sorted(car.price_usd for car in matches if car.price_usd > 0)

        if len(prices) < 3:
            return None, None, None, len(prices)

        return float(median(prices)), float(prices[0]), float(prices[-1]), len(prices)

    def _apply_sanity_cap(self, estimate: float, request: UsedCarPricePredictionRequest) -> float:
        if request.vehicle_age >= 10 or request.km_driven >= 150000:
            return min(estimate, 18000.0)
        if request.vehicle_age >= 7 or request.km_driven >= 100000:
            return min(estimate, 26000.0)
        return estimate

    def predict(
        self,
        request: UsedCarPricePredictionRequest,
        db: Session | None = None,
    ) -> UsedCarPricePredictionResponse:
        if self.model is None:
            raise RuntimeError("Used-car price estimator model is not available.")

        row = pd.DataFrame(
            [
                {
                    "brand": request.brand,
                    "model": request.model,
                    "vehicle_age": request.vehicle_age,
                    "km_driven": request.km_driven,
                    "seller_type": request.seller_type,
                    "fuel_type": request.fuel_type,
                    "transmission_type": request.transmission_type,
                    "mileage": request.mileage,
                    "engine": request.engine,
                    "max_power": request.max_power,
                    "seats": request.seats,
                }
            ]
        )

        ml_estimated_price = float(self.model.predict(row)[0])
        inventory_median, inventory_low, inventory_high, match_count = self._inventory_reference(db, request)

        if inventory_median is not None:
            estimated_price = (ml_estimated_price * 0.6) + (inventory_median * 0.4)
            calibration_note = (
                f"Calibrated with {match_count} similar used cars from the AutoAdvisor inventory "
                f"(60% ML baseline, 40% inventory median)."
            )
        else:
            estimated_price = ml_estimated_price
            calibration_note = (
                "ML baseline only: not enough similar used cars were found in the AutoAdvisor inventory "
                "for calibration."
            )

        estimated_price = self._apply_sanity_cap(estimated_price, request)

        mae = float(self.mae_usd or 0)
        inventory_spread = 0.0
        if inventory_low is not None and inventory_high is not None:
            inventory_spread = max(abs(estimated_price - inventory_low), abs(inventory_high - estimated_price))

        margin = max(mae, estimated_price * 0.15, inventory_spread * 0.5)

        low_estimate = max(0.0, estimated_price - margin)
        high_estimate = estimated_price + margin

        return UsedCarPricePredictionResponse(
            ml_estimated_price_usd=round(ml_estimated_price, 2),
            inventory_reference_price_usd=round(inventory_median, 2) if inventory_median is not None else None,
            estimated_price_usd=round(estimated_price, 2),
            fair_price_low_usd=round(low_estimate, 2),
            fair_price_high_usd=round(high_estimate, 2),
            low_estimate_usd=round(low_estimate, 2),
            high_estimate_usd=round(high_estimate, 2),
            model_mae_usd=round(float(self.mae_usd), 2) if self.mae_usd is not None else None,
            model_r2=round(float(self.r2), 3) if self.r2 is not None else None,
            calibration_note=calibration_note,
            disclaimer=(
                "This is a baseline ML estimate for used cars only. "
                "It may be blended with similar curated demo inventory cars when enough matches exist, "
                "but inspection condition, accident history, local demand, "
                "customs, and dealer margins can change the real market price."
            ),
        )


price_estimator = UsedCarPriceEstimator()
