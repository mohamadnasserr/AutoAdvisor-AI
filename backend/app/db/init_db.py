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


def init_db() -> None:
    Base.metadata.create_all(bind=engine)
    ensure_car_image_url_column()


if __name__ == "__main__":
    init_db()
    print("Database tables created successfully.")
