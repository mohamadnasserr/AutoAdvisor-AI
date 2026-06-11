from pathlib import Path

import joblib
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


DATA_PATH = Path("data/raw/used_cars_kaggle.csv")
MODEL_DIR = Path("models")
MODEL_PATH = MODEL_DIR / "used_car_price_estimator.joblib"

INR_TO_USD_RATE = 83.0


def train_price_estimator() -> None:
    if not DATA_PATH.exists():
        raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    required_columns = [
        "brand",
        "model",
        "vehicle_age",
        "km_driven",
        "seller_type",
        "fuel_type",
        "transmission_type",
        "mileage",
        "engine",
        "max_power",
        "seats",
        "selling_price",
    ]

    missing_columns = [column for column in required_columns if column not in df.columns]
    if missing_columns:
        raise ValueError(f"Missing required columns: {missing_columns}")

    df = df[required_columns].copy()
    df = df.dropna()

    df["price_usd"] = df["selling_price"] / INR_TO_USD_RATE

    features = [
        "brand",
        "model",
        "vehicle_age",
        "km_driven",
        "seller_type",
        "fuel_type",
        "transmission_type",
        "mileage",
        "engine",
        "max_power",
        "seats",
    ]

    target = "price_usd"

    x = df[features]
    y = df[target]

    categorical_features = [
        "brand",
        "model",
        "seller_type",
        "fuel_type",
        "transmission_type",
    ]

    numeric_features = [
        "vehicle_age",
        "km_driven",
        "mileage",
        "engine",
        "max_power",
        "seats",
    ]

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                categorical_features,
            ),
            (
                "numeric",
                "passthrough",
                numeric_features,
            ),
        ]
    )

    model = RandomForestRegressor(
        n_estimators=250,
        random_state=42,
        min_samples_leaf=2,
        n_jobs=-1,
    )

    pipeline = Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("model", model),
        ]
    )

    x_train, x_test, y_train, y_test = train_test_split(
        x,
        y,
        test_size=0.2,
        random_state=42,
    )

    pipeline.fit(x_train, y_train)

    predictions = pipeline.predict(x_test)

    mae = mean_absolute_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "model": pipeline,
            "features": features,
            "target": target,
            "currency": "USD",
            "source_currency": "INR",
            "inr_to_usd_rate": INR_TO_USD_RATE,
            "mae_usd": mae,
            "r2": r2,
        },
        MODEL_PATH,
    )

    print("Used-car price estimator trained successfully.")
    print(f"Rows used: {len(df)}")
    print(f"Saved model to: {MODEL_PATH}")
    print(f"MAE USD: {mae:.2f}")
    print(f"R2: {r2:.3f}")


if __name__ == "__main__":
    train_price_estimator()