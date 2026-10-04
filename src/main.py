"""FastAPI application entry point.

Run from the project root with:

    uvicorn src.main:app --reload
"""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from .calculator import ExpressionError
from .controller import calculate_controller, history_controller
from .database import init_db


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Create the database table (and file) before serving requests."""
    init_db()
    yield


app = FastAPI(
    title="Calculator Backend",
    description="Front-end/back-end separated calculator: back-end expression "
    "evaluation, validation and history persistence.",
    version="1.0.0",
    lifespan=lifespan,
)

# The front end is a separate project served from a different origin, so CORS
# must allow cross-origin requests. Tighten this in production if needed.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(calculate_controller.router)
app.include_router(history_controller.router)


@app.get("/", tags=["meta"])
def root() -> dict:
    return {"service": "calculator-backend", "status": "ok"}


@app.get("/api/health", tags=["meta"])
def health() -> dict:
    return {"status": "ok"}


@app.exception_handler(ExpressionError)
async def expression_error_handler(_: Request, exc: ExpressionError) -> JSONResponse:
    """Invalid expressions / division by zero -> 400 with a clear message."""
    return JSONResponse(
        status_code=400, content={"success": False, "message": str(exc)}
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
    _: Request, exc: StarletteHTTPException
) -> JSONResponse:
    """Keep a consistent error shape for HTTP errors (e.g. 404)."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"success": False, "message": exc.detail},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    _: Request, exc: RequestValidationError
) -> JSONResponse:
    """Missing / wrongly typed body -> 422 with the same error shape."""
    return JSONResponse(
        status_code=422,
        content={"success": False, "message": "Invalid request body"},
    )
