"""Database access for calculation history records."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Dict, List

from ..calculator import format_result
from ..database import connection

TIMESTAMP_FORMAT = "%Y-%m-%d %H:%M:%S"


def save(expression: str, result: Decimal) -> Dict[str, object]:
    """Insert one history record and return it."""
    created_at = datetime.now().strftime(TIMESTAMP_FORMAT)
    result_text = format_result(result)

    with connection() as conn:
        cursor = conn.execute(
            "INSERT INTO calculation_history (expression, result, created_at) "
            "VALUES (?, ?, ?)",
            (expression, result_text, created_at),
        )
        new_id = int(cursor.lastrowid)

    return {
        "id": new_id,
        "expression": expression,
        "result": result_text,
        "created_at": created_at,
    }


def list_all() -> List[Dict[str, object]]:
    """Return every history record, newest first."""
    with connection() as conn:
        rows = conn.execute(
            "SELECT id, expression, result, created_at "
            "FROM calculation_history ORDER BY id DESC"
        ).fetchall()
    return [dict(row) for row in rows]


def delete_one(record_id: int) -> int:
    """Delete a single record, returning the number of deleted rows."""
    with connection() as conn:
        cursor = conn.execute(
            "DELETE FROM calculation_history WHERE id = ?", (record_id,)
        )
        return int(cursor.rowcount)


def delete_all() -> int:
    """Delete every record, returning the number of deleted rows."""
    with connection() as conn:
        cursor = conn.execute("DELETE FROM calculation_history")
        return int(cursor.rowcount)
