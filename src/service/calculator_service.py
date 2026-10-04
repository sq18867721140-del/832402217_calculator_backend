"""Calculation orchestration: evaluate on the back end, then persist."""

from __future__ import annotations

from typing import Dict

from ..calculator import evaluate, to_number
from . import history_service


def calculate(expression: str) -> Dict[str, object]:
    """Evaluate *expression* on the back end and store the record."""
    value = evaluate(expression)
    record = history_service.save(expression.strip(), value)
    return {
        "id": record["id"],
        "expression": record["expression"],
        "result": to_number(value),
    }
