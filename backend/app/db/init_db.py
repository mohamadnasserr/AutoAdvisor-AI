from backend.app.db.database import Base, engine
from backend.app.models import db_models  # noqa: F401


def init_db() -> None:
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("Database tables created successfully.")