"""HTTP route for evaluating an expression."""

from __future__ import annotations

from fastapi import APIRouter

from ..model.history import CalculateRequest, CalculateResponse
from ..service import calculator_service

router = APIRouter(prefix="/api", tags=["calculate"])


@router.post("/calculate", response_model=CalculateResponse)
def calculate(payload: CalculateRequest) -> CalculateResponse:
    """Evaluate the expression on the back end, store it and return the result.

    ``ExpressionError`` raised by the calculator is converted into a
    ``400 Bad Request`` JSON response by the global handler in ``main``.
    """
    result = calculator_service.calculate(payload.expression)
    return CalculateResponse(**result)
