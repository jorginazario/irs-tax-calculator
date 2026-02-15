"""Map custom exceptions to HTTP status codes."""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from starlette.requests import Request

from src.models.exceptions import (
    InvalidFilingStatusError,
    MissingIncomeDataError,
    NegativeIncomeError,
    TaxCalculatorError,
    UnsupportedScenarioError,
)


def register_exception_handlers(app: FastAPI) -> None:
    """Attach all custom exception handlers to the FastAPI app."""

    @app.exception_handler(InvalidFilingStatusError)
    async def _invalid_filing_status(request: Request, exc: InvalidFilingStatusError):
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.exception_handler(MissingIncomeDataError)
    async def _missing_income(request: Request, exc: MissingIncomeDataError):
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.exception_handler(NegativeIncomeError)
    async def _negative_income(request: Request, exc: NegativeIncomeError):
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @app.exception_handler(UnsupportedScenarioError)
    async def _unsupported_scenario(request: Request, exc: UnsupportedScenarioError):
        return JSONResponse(status_code=400, content={"detail": str(exc)})

    @app.exception_handler(TaxCalculatorError)
    async def _tax_calculator_base(request: Request, exc: TaxCalculatorError):
        return JSONResponse(status_code=500, content={"detail": str(exc)})

    @app.exception_handler(ValueError)
    async def _value_error(request: Request, exc: ValueError):
        return JSONResponse(status_code=422, content={"detail": str(exc)})
