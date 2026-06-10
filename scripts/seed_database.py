import pandas as pd

from backend.app.db.database import SessionLocal
from backend.app.db.init_db import init_db
from backend.app.models.db_models import Car, Dealership


def clean_optional_string(value):
    if pd.isna(value) or value == "":
        return None
    return str(value)


def clean_optional_float(value):
    if pd.isna(value) or value == "":
        return None
    return float(value)


def clean_optional_int(value):
    if pd.isna(value) or value == "":
        return None
    return int(value)


def get_or_create_dealer(db, row) -> Dealership:
    dealer_name = row["dealer_name"]

    dealer = (
        db.query(Dealership)
        .filter(Dealership.name == dealer_name)
        .first()
    )

    if dealer is not None:
        return dealer

    dealer = Dealership(
        name=dealer_name,
        location=row["region"],
        phone="+961 demo number",
        email=f"{dealer_name.lower().replace(' ', '')}@demo.com",
        website=None,
        supported_brands=row["make"],
        region="Lebanon",
    )

    db.add(dealer)
    db.flush()

    return dealer


def car_exists(db, row) -> bool:
    existing_car = (
        db.query(Car)
        .filter(
            Car.listing_type == row["listing_type"],
            Car.make == row["make"],
            Car.model == row["model"],
            Car.trim == clean_optional_string(row.get("trim")),
            Car.year == int(row["year"]),
            Car.price_usd == float(row["price_usd"]),
            Car.region == row["region"],
        )
        .first()
    )

    return existing_car is not None


def seed_database() -> None:
    init_db()

    db = SessionLocal()

    try:
        df = pd.read_csv("data/seed/cars.csv")

        inserted_cars = 0
        skipped_cars = 0

        for _, row in df.iterrows():
            dealer = get_or_create_dealer(db, row)

            if car_exists(db, row):
                skipped_cars += 1
                continue

            car = Car(
                listing_type=row["listing_type"],
                is_new=str(row["is_new"]).lower() == "true",
                make=row["make"],
                model=row["model"],
                trim=clean_optional_string(row.get("trim")),
                year=int(row["year"]),
                price_usd=float(row["price_usd"]),
                mileage_km=clean_optional_int(row.get("mileage_km")),
                body_type=row["body_type"],
                fuel=row["fuel"],
                transmission=row["transmission"],
                color=clean_optional_string(row.get("color")),
                condition=clean_optional_string(row.get("condition")),
                warranty_years=clean_optional_float(row.get("warranty_years")),
                region=row["region"],
                dealer_id=dealer.id,
            )

            db.add(car)
            inserted_cars += 1

        db.commit()

        total_cars = db.query(Car).count()
        total_dealers = db.query(Dealership).count()

        print("Seed database completed successfully.")
        print(f"Inserted cars: {inserted_cars}")
        print(f"Skipped existing cars: {skipped_cars}")
        print(f"Total cars in database: {total_cars}")
        print(f"Total dealerships in database: {total_dealers}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()