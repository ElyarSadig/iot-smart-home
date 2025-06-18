from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from pathlib import Path
from fastapi import Form

room_data = {
    "A": {
        "sensor": {"Temp": 23.0, "RelH": 45, "Occ": 1, "Act": 2, "Door": 0, "Win": 1, "L1": 500, "L2": 700},
        "preference": 24.0
    },
    "B": {
        "sensor": {"Temp": 22.5, "RelH": 42, "Occ": 2, "Act": 3, "Door": 1, "Win": 0, "L1": 480, "L2": 720},
        "preference": 23.5
    },
    "C": {
        "sensor": {"Temp": 24.1, "RelH": 50, "Occ": 1, "Act": 1, "Door": 0, "Win": 1, "L1": 510, "L2": 690},
        "preference": 25.0
    }
}

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

@router.get("/room/{room_id}/sensors", response_class=HTMLResponse)
async def get_sensor_form(request: Request, room_id: str):
    sensor = room_data[room_id]["sensor"]
    return templates.TemplateResponse("_sensors_form.html", {
        "request": request,
        "sensor": sensor,
        "room_id": room_id
    })

@router.post("/room/{room_id}/sensors", response_class=HTMLResponse)
async def update_sensor_form(
    request: Request,
    room_id: str,
    Temp: float = Form(...),
    RelH: float = Form(...),
    Occ: int = Form(...),
    Act: int = Form(...),
    Door: int = Form(...),
    Win: int = Form(...),
    L1: int = Form(...),
    L2: int = Form(...)
):
    room_data[room_id]["sensor"] = {
        "Temp": Temp, "RelH": RelH, "Occ": Occ, "Act": Act,
        "Door": Door, "Win": Win, "L1": L1, "L2": L2
    }
    return await get_sensor_form(request, room_id)

@router.get("/room/{room_id}/predict", response_class=HTMLResponse)
async def predict_temp(request: Request, room_id: str):
    sensor = room_data[room_id]["sensor"]
    prediction = round(sensor["Temp"] + 0.3 * sensor["Occ"] - 0.2 * sensor["Door"], 1)
    return templates.TemplateResponse("_predicted_temp.html", {
        "request": request,
        "predicted_temp": prediction
    })

@router.get("/room/{room_id}/preference", response_class=HTMLResponse)
async def get_preference(request: Request, room_id: str):
    return templates.TemplateResponse("_preference_form.html", {
        "request": request,
        "preference_temp": room_data[room_id]["preference"],
        "room_id": room_id
    })

@router.post("/room/{room_id}/preference", response_class=HTMLResponse)
async def update_preference(request: Request, room_id: str, preference: float = Form(...)):
    room_data[room_id]["preference"] = preference
    return await get_preference(request, room_id)


@router.post("/room/{room_id}/optimize", response_class=HTMLResponse)
async def optimize_room(request: Request, room_id: str):
    # Simulate optimization: set Temp to preferred, adjust others slightly
    preference = room_data[room_id]["preference"]
    optimized_sensor = {
        "Temp": round(preference, 1),
        "RelH": 40 + (preference % 10),  # Fake logic
        "Occ": 1,
        "Act": 2,
        "Door": 0,
        "Win": 0,
        "L1": 550,
        "L2": 770
    }

    room_data[room_id]["sensor"] = optimized_sensor

    return templates.TemplateResponse("_sensors_form.html", {
        "request": request,
        "sensor": optimized_sensor,
        "room_id": room_id
    })