"""FastAPI application — IRS Tax Calculator."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.exception_handlers import register_exception_handlers
from src.api.routes import router

app = FastAPI(
    title="IRS Tax Calculator",
    version="0.1.0",
    description="Federal tax calculator for tax year 2024",
)

# CORS — allow the Vite dev server and preview server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:4173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

register_exception_handlers(app)

app.include_router(router, prefix="/api")
