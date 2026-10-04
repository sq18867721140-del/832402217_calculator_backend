"""SQLite connection helpers and schema initialization."""

from __future__ import annotations

import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

# Default location: <project root>/data/calculator.db
# Can be overridden with the DATABASE_PATH environment variable.
BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB_PATH = BASE_DIR / "data" / "calculator.db"
DB_PATH = Path(os.getenv("DATABASE_PATH", str(DEFAULT_DB_PATH)))


def get_connection() -> sqlite3.Connection:
    """Create a new SQLite connection with row access by column name."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


@contextmanager
def connection():
    """Context manager that commits on success and always closes."""
    conn = get_connection()
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    """Create the calculation history table if it does not exist yet."""
    with connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS calculation_history (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                expression  TEXT    NOT NULL,
                result      TEXT    NOT NULL,
                created_at  TEXT    NOT NULL
            )
            """
        )
        conn.execute(
            "CREATE INDEX IF NOT EXISTS idx_history_created_at "
            "ON calculation_history (created_at)"
        )
