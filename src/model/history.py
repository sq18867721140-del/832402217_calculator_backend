"""Pydantic schemas shared by the API layer."""

from __future__ import annotations

from typing import Union

from pydantic import BaseModel, Field

Number = Union[int, float]


class CalculateRequest(BaseModel):
    expression: str = Field(..., description="Arithmetic expression, e.g. '(1+2)*3'")

    model_config = {
        "json_schema_extra": {"examples": [{"expression": "(1+2)*3"}]},
    }


class CalculateResponse(BaseModel):
    success: bool = True
    id: int = Field(..., description="Id of the stored history record")
    expression: str
    result: Number


class HistoryItem(BaseModel):
    id: int
    expression: str
    result: Number
    created_at: str


class DeleteResponse(BaseModel):
    success: bool = True
    deleted: int


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
