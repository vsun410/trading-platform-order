"""FastAPI application entry point for Dashboard V2.

This module initializes the FastAPI app with Jinja2 templates,
static files, and all required routers.
"""

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from loguru import logger

from src.dashboard_v2.config import settings
from src.dashboard_v2.routers import api, pages

# Paths
BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
STATIC_DIR = BASE_DIR / "static"

# Initialize FastAPI app
app = FastAPI(
    title="KimpTrade Dashboard V2",
    description="FastAPI + Jinja2 based monitoring dashboard for KimpTrade",
    version="0.1.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Jinja2 templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Include routers
app.include_router(api.router)
app.include_router(pages.router)


@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logger.info("Dashboard V2 starting up...")
    logger.info(f"Debug mode: {settings.debug}")
    logger.info(f"Refresh interval: {settings.refresh_interval}s")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info("Dashboard V2 shutting down...")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.dashboard_v2.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
