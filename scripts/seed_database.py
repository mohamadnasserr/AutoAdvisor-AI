import pandas as pd

from backend.app.db.database import SessionLocal
from backend.app.db.init_db import init_db
from backend.app.models.db_models import Car, Dealership


DEMO_DEALER_CONTACTS = {
    "Beirut Auto Hub": ("+961-1-000001", "beirutautohub@demo.invalid"),
    "Cedar Motors": ("+961-9-000002", "cedarmotors@demo.invalid"),
    "Levant Auto Gallery": ("+961-5-000003", "levantautogallery@demo.invalid"),
    "North Coast Motors": ("+961-6-000004", "northcoastmotors@demo.invalid"),
    "South Gate Auto": ("+961-7-000005", "southgateauto@demo.invalid"),
    "Bekaa Drive Center": ("+961-8-000006", "bekaadrivecenter@demo.invalid"),
    "Nabatieh Auto Point": ("+961-7-000007", "nabatiehautopoint@demo.invalid"),
    "Byblos Motor House": ("+961-9-000008", "byblosmotorhouse@demo.invalid"),
    "Baabda Car Center": ("+961-5-000009", "baabdacarcenter@demo.invalid"),
    "Keserwan Mobility": ("+961-9-000010", "keserwanmobility@demo.invalid"),
}

LEGACY_DEALER_RENAMES = {
    "Beirut Auto": "Beirut Auto Hub",
    "Auto House": "Bekaa Drive Center",
    "Premium Cars": "Keserwan Mobility",
    "North Motors": "North Coast Motors",
    "South Auto": "South Gate Auto",
}


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
    phone, email = DEMO_DEALER_CONTACTS.get(
        dealer_name,
        ("+961-1-000000", "inventory@demo.invalid"),
    )

    dealer = (
        db.query(Dealership)
        .filter(Dealership.name == dealer_name)
        .first()
    )

    if dealer is not None:
        dealer.location = row["region"]
        dealer.phone = phone
        dealer.email = email
        dealer.supported_brands = row["make"]
        dealer.region = "Lebanon"
        return dealer

    dealer = Dealership(
        name=dealer_name,
        location=row["region"],
        phone=phone,
        email=email,
        website=None,
        supported_brands=row["make"],
        region="Lebanon",
    )

    db.add(dealer)
    db.flush()

    return dealer


def align_legacy_demo_dealers(db) -> None:
    for legacy_name, current_name in LEGACY_DEALER_RENAMES.items():
        legacy_dealer = (
            db.query(Dealership)
            .filter(Dealership.name == legacy_name)
            .first()
        )
        current_dealer = (
            db.query(Dealership)
            .filter(Dealership.name == current_name)
            .first()
        )

        if legacy_dealer is not None and current_dealer is None:
            legacy_dealer.name = current_name


def find_existing_car(db, row) -> Car | None:
    return (
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


def apply_seed_values(car: Car, row, dealer: Dealership) -> None:
    car.is_new = str(row["is_new"]).lower() == "true"
    car.mileage_km = clean_optional_int(row.get("mileage_km"))
    car.body_type = row["body_type"]
    car.fuel = row["fuel"]
    car.transmission = row["transmission"]
    car.color = clean_optional_string(row.get("color"))
    car.condition = clean_optional_string(row.get("condition"))
    car.warranty_years = clean_optional_float(row.get("warranty_years"))
    car.availability_status = clean_optional_string(
        row.get("availability_status")
    ) or "available"
    car.platform_source = clean_optional_string(
        row.get("platform_source")
    ) or "curated_demo_seed"
    car.image_url = clean_optional_string(row.get("image_url"))
    car.dealer_id = dealer.id


def seed_database() -> None:
    init_db()

    db = SessionLocal()

    try:
        df = pd.read_csv("data/seed/cars.csv")
        align_legacy_demo_dealers(db)

        inserted_cars = 0
        skipped_cars = 0
        updated_image_urls = 0

        for _, row in df.iterrows():
            dealer = get_or_create_dealer(db, row)

            existing_car = find_existing_car(db, row)

            if existing_car is not None:
                seed_image_url = clean_optional_string(row.get("image_url"))
                if existing_car.image_url != seed_image_url:
                    updated_image_urls += 1
                apply_seed_values(existing_car, row, dealer)
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
                availability_status=clean_optional_string(
                    row.get("availability_status")
                ) or "available",
                platform_source=clean_optional_string(
                    row.get("platform_source")
                ) or "curated_demo_seed",
                image_url=clean_optional_string(row.get("image_url")),
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
        print(f"Existing car image URLs updated: {updated_image_urls}")
        print(f"Total cars in database: {total_cars}")
        print(f"Total dealerships in database: {total_dealers}")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()
