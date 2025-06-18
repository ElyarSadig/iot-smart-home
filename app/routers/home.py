from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from pathlib import Path
from app.routers.room import room_data

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))

@router.get("/")
async def get_home(request: Request):
    rooms = [{"id": room_id, **room_data[room_id]} for room_id in room_data]
    return templates.TemplateResponse("home.html", {
        "request": request,
        "rooms": rooms
    })
