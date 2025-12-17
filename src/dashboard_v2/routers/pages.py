"""Pages router for Dashboard V2.

Serves HTML pages using Jinja2 templates.
"""

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.dashboard_v2.config import settings

router = APIRouter(tags=["pages"])

# Templates directory
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Render main dashboard page."""
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "title": "KimpTrade Dashboard",
            "refresh_interval": settings.refresh_interval,
        },
    )
