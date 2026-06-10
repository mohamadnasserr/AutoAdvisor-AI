import os
import sqlite3
from pathlib import Path

DEFAULT_DATABASE_PATH = Path(__file__).resolve().parents[2] / "data" / "autoadvisor.db"


def get_database_path() -> Path:
    return Path(os.getenv("DATABASE_PATH", DEFAULT_DATABASE_PATH))


def get_connection() -> sqlite3.Connection:
    database_path = get_database_path()
    database_path.parent.mkdir(parents=True, exist_ok=True)

    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    return connection
