"""FastAPI application — IRS Tax Calculator."""

from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI

# Load .env from project root (one level above backend/)
load_dotenv(Path(__file__).resolve().parent.parent.parent.parent / ".env")
from fastapi.middleware.cors import CORSMiddleware

from src.api.analysis_routes import analysis_router
from src.api.exception_handlers import register_exception_handlers
from src.api.routes import router
from src.database.db import close_db, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialise the SQLite database on startup and close on shutdown."""
    init_db()
    yield
    close_db()


app = FastAPI(
    title="IRS Tax Calculator",
    version="0.1.0",
    description="Federal tax calculator for tax year 2024",
    lifespan=lifespan,
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
app.include_router(analysis_router, prefix="/api")
