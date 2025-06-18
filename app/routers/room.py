from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))

@router.get("/room/{room_id}", response_class=HTMLResponse)
async def room_page(request: Request, room_id: str):
    # Mock sensor data
    sensor = {
        "Temp": 23.5,
        "RelH": 45,
        "Occ": 1,
        "Act": 2,
        "Door": 0,
        "Win": 1,
        "L1": 550,
        "L2": 760,
    }
    preference = 24.5
    prediction = 23.8
    return templates.TemplateResponse("room.html", {
        "request": request,
        "room_id": room_id,
        "sensor": sensor,
        "prediction": prediction,
        "preference": preference,
    })
