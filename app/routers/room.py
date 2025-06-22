from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.database.models import SensorData, ComfortPreference, RoomPreference
from datetime import datetime
from pathlib import Path
from fastapi import Form

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))

@router.get("/room/{room_id}", response_class=HTMLResponse)
async def room_page(request: Request, room_id: str):
    return templates.TemplateResponse("room.html", {
        "request": request,
        "room_id": room_id,
    })

@router.get("/room/{room_id}/sensors", response_class=HTMLResponse)
async def get_sensor_form(request: Request, room_id: str):
    async with AsyncSessionLocal() as session:
        stmt = (
            select(SensorData)
            .where(SensorData.room == room_id)
            .order_by(SensorData.created_at.desc())
        )
        result = await session.execute(stmt)
        sensor_row = result.scalars().first()

        if not sensor_row:
            return HTMLResponse(
                content=f"<p class='text-red-500'>❌ No sensor data found for room {room_id}.</p>",
                status_code=404
            )

        sensor = {
            "Temp": sensor_row.Temp,
            "RelH": sensor_row.RelH,
            "Occ": sensor_row.Occ,
            "Act": sensor_row.Act,
            "Door": sensor_row.Door,
            "Win": sensor_row.Win,
            "L1": sensor_row.L1,
            "L2": sensor_row.L2,
        }

        return templates.TemplateResponse("_sensors_form.html", {
            "request": request,
            "sensor": sensor,
            "room_id": room_id
        })


@router.post("/room/{room_id}/sensors", response_class=HTMLResponse)
async def update_sensor_form(
    request: Request,
    room_id: str,
    RelH: float = Form(...),
    Occ: int = Form(...),
    Act: int = Form(...),
    Door: int = Form(...),
    Win: int = Form(...),
    L1: int = Form(...),
    L2: int = Form(...)
):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(SensorData)
            .where(SensorData.room == room_id)
            .order_by(SensorData.created_at.desc())
            .limit(1)
        )
        sensor = result.scalar_one_or_none()

        if sensor:
            sensor.RelH = RelH
            sensor.Occ = Occ
            sensor.Act = Act
            sensor.Door = Door
            sensor.Win = Win
            sensor.L1 = L1
            sensor.L2 = L2
            sensor.created_at = datetime.now()

        await session.commit()

    return await get_sensor_form(request, room_id)


@router.get("/room/{room_id}/predict", response_class=HTMLResponse)
async def predict_temp(request: Request, room_id: str):
    # TODO load from the trained model to predict the room temperature based on KNN!
    prediction = 23.5
    return templates.TemplateResponse("_predicted_temp.html", {
        "request": request,
        "predicted_temp": prediction
    })


@router.get("/room/{room_id}/preference", response_class=HTMLResponse)
async def get_preference(request: Request, room_id: str):
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(RoomPreference)
            .where(RoomPreference.room == room_id)
            .order_by(RoomPreference.created_at.desc())
            .limit(1)
        )
        pref = result.scalar_one_or_none()

    return templates.TemplateResponse("_preference_form.html", {
        "request": request,
        "preference_temp": pref.temperature,
        "room_id": room_id
    })


@router.post("/room/{room_id}/preference", response_class=HTMLResponse)
async def insert_preference(request: Request, room_id: str, preference: float = Form(...)):
    async with AsyncSessionLocal() as session:
        new_pref = ComfortPreference(
            room=room_id,
            temperature=preference
        )
        session.add(new_pref)
        await session.commit()

    from .room import get_preference
    return await get_preference(request, room_id)


@router.post("/room/{room_id}/optimize", response_class=HTMLResponse)
async def optimize_room(request: Request, room_id: str):
    preference = 22
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

    return templates.TemplateResponse("_sensors_form.html", {
        "request": request,
        "sensor": optimized_sensor,
        "room_id": room_id
    })