from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))

@router.get("/")
async def get_home(request: Request):
    rooms = ["A", "B", "C"]
    return templates.TemplateResponse("home.html", {"request": request, "rooms": rooms})
