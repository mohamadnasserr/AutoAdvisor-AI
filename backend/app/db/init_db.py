from sqlalchemy import inspect, text

from backend.app.db.database import Base, engine
from backend.app.models import db_models  # noqa: F401


def ensure_car_image_url_column() -> None:
    column_names = {
        column["name"] for column in inspect(engine).get_columns("cars")
    }

    if "image_url" not in column_names:
        with engine.begin() as connection:
            connection.execute(
                text("ALTER TABLE cars ADD COLUMN image_url VARCHAR(500)")
            )


def ensure_dealer_lead_contact_columns() -> None:
    statements = [
        "ALTER TABLE dealer_leads ADD COLUMN IF NOT EXISTS customer_name VARCHAR(150)",
        "ALTER TABLE dealer_leads ADD COLUMN IF NOT EXISTS customer_phone VARCHAR(80)",
        "ALTER TABLE dealer_leads ADD COLUMN IF NOT EXISTS customer_email VARCHAR(150)",
        "ALTER TABLE dealer_leads ADD COLUMN IF NOT EXISTS notes TEXT",
    ]

    with engine.begin() as connection:
        for statement in statements:
            connection.execute(text(statement))


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    ensure_car_image_url_column()
    ensure_dealer_lead_contact_columns()


if __name__ == "__main__":
    init_db()
    print("Database tables created successfully.")
