from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import logging


router = APIRouter(prefix="/miniapp", tags=["miniapp"])

templates = Jinja2Templates(directory="./templates")

logger = logging.getLogger("miniapp_logger")


@router.get("/{user_id}", response_class=HTMLResponse)
async def read_root(user_id, request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request, "user_id": user_id}
    )
