from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.db.database import SessionLocal  # noqa: E402
from backend.app.db.init_db import init_db  # noqa: E402
from backend.app.models.db_models import DealerLead  # noqa: E402


def reset_demo_leads() -> int:
    init_db()
    db = SessionLocal()

    try:
        deleted_count = db.query(DealerLead).delete(synchronize_session=False)
        db.commit()
        return deleted_count
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    deleted = reset_demo_leads()
    print(f"Deleted dealer leads: {deleted}")
