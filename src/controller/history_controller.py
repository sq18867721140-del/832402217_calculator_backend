"""HTTP routes for reading and deleting calculation history."""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, HTTPException

from ..calculator import to_number_from_text
from ..model.history import DeleteResponse, HistoryItem
from ..service import history_service

router = APIRouter(prefix="/api", tags=["history"])


def _to_item(record: dict) -> HistoryItem:
    return HistoryItem(
        id=record["id"],
        expression=record["expression"],
        result=to_number_from_text(str(record["result"])),
        created_at=record["created_at"],
    )


@router.get("/history", response_model=List[HistoryItem])
def get_history() -> List[HistoryItem]:
    """Return the full calculation history, newest first."""
    return [_to_item(record) for record in history_service.list_all()]


@router.delete("/history/{record_id}", response_model=DeleteResponse)
def delete_history(record_id: int) -> DeleteResponse:
    """Delete one history record by id."""
    deleted = history_service.delete_one(record_id)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="History record not found")
    return DeleteResponse(success=True, deleted=deleted)


@router.delete("/history", response_model=DeleteResponse)
def clear_history() -> DeleteResponse:
    """Optional extended feature: delete all history records."""
    deleted = history_service.delete_all()
    return DeleteResponse(success=True, deleted=deleted)
