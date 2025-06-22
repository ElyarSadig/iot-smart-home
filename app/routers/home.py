from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from pathlib import Path
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.database.models import SensorData, ComfortPreference

router = APIRouter()
templates = Jinja2Templates(directory=str(Path(__file__).resolve().parent.parent / "templates"))

@router.get("/")
async def get_home(request: Request):
    rooms = []

    async with AsyncSessionLocal() as session:
        sensor_stmt = (
            select(SensorData)
            .distinct(SensorData.room)
            .order_by(SensorData.room, SensorData.created_at.desc())
        )
        sensor_rows = (await session.execute(sensor_stmt)).scalars().all()

        pref_stmt = (
            select(ComfortPreference)
            .distinct(ComfortPreference.room)
            .order_by(ComfortPreference.room, ComfortPreference.created_at.desc())
        )
        pref_rows = (await session.execute(pref_stmt)).scalars().all()

        pref_map = {p.room: p.temperature for p in pref_rows}

        for row in sensor_rows:
            rooms.append({
                "id": row.room,
                "Temp": row.Temp,
                "RelH": row.RelH,
                "Occ": row.Occ,
                "Act": row.Act,
                "Door": row.Door,
                "Win": row.Win,
                "Comfort": pref_map.get(row.room, None),
                "Prediction": round(row.Temp, 1)  # Mock predicted temp
            })

    return templates.TemplateResponse("home.html", {
        "request": request,
        "rooms": rooms
    })
