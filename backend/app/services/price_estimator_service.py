from pathlib import Path

import joblib
import pandas as pd

from backend.app.config import settings
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

    def predict(self, request: UsedCarPricePredictionRequest) -> UsedCarPricePredictionResponse:
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

        estimated_price = float(self.model.predict(row)[0])

        mae = float(self.mae_usd or 0)
        lower_margin = max(mae, estimated_price * 0.12)
        upper_margin = max(mae, estimated_price * 0.12)

        low_estimate = max(0.0, estimated_price - lower_margin)
        high_estimate = estimated_price + upper_margin

        return UsedCarPricePredictionResponse(
            estimated_price_usd=round(estimated_price, 2),
            low_estimate_usd=round(low_estimate, 2),
            high_estimate_usd=round(high_estimate, 2),
            model_mae_usd=round(float(self.mae_usd), 2) if self.mae_usd is not None else None,
            model_r2=round(float(self.r2), 3) if self.r2 is not None else None,
            disclaimer=(
                "This is a baseline ML estimate for used cars only. "
                "It is trained on a public used-car dataset and converted to USD, "
                "so local Lebanon/MENA market calibration, inspection condition, accident history, "
                "customs, and dealer margins can change the real market price."
            ),
        )


price_estimator = UsedCarPriceEstimator()