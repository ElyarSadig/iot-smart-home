from fastapi import APIRouter, Request, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy import select
from app.database import AsyncSessionLocal
from app.database.models import SensorData, ComfortPreference, RoomPreference
from datetime import datetime
from pathlib import Path
from fastapi import Form
from app.model_registery import model_registry
import pandas as pd
from scipy.optimize import differential_evolution
import numpy as np

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
                content=f"<p class='text-red-500'> No sensor data found for room {room_id}.</p>",
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
    L1: float = Form(...),
    L2: float = Form(...)
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
    model_key = f"knn_{room_id}"
    model = model_registry.get(model_key)

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(SensorData)
            .where(SensorData.room == room_id)
            .order_by(SensorData.created_at.desc())
            .limit(1)
        )
        sensor = result.scalar_one_or_none()

        # Prepare feature dictionary using correct names
        features_dict = {
            "RelH": sensor.RelH,
            "L1": sensor.L1,
            "L2": sensor.L2,
            "Occ": sensor.Occ,
            "Act": sensor.Act,
            "Door": sensor.Door,
            "Win": sensor.Win
        }

        input_df = pd.DataFrame([features_dict])
        prediction = model.predict(input_df)[0]

    return templates.TemplateResponse("_predicted_temp.html", {
        "request": request,
        "predicted_temp": round(prediction, 2)
    })


@router.get("/room/{room_id}/preference", response_class=HTMLResponse)
async def get_preference(request: Request, room_id: str):
    model_key = f"rf_{room_id.upper()}"
    model = model_registry.get(model_key)

    if model is None:
        raise HTTPException(status_code=500, detail=f"Model not loaded for room: {room_id}")

    now = datetime.now()
    input_df = pd.DataFrame([{
        "hour": now.hour,
        "minute": now.minute,
        "dayofweek": now.weekday()
    }])

    try:
        prediction = model.predict(input_df)[0]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

    return templates.TemplateResponse("_preference_form.html", {
        "request": request,
        "preference_temp": round(prediction, 2),
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
    rf_model = model_registry.get(f"rf_{room_id.upper()}")
    knn_model = model_registry.get(f"knn_{room_id.upper()}")

    if rf_model is None or knn_model is None:
        raise HTTPException(status_code=500, detail="Model(s) not loaded for this room.")

    now = datetime.now()
    hour = now.hour
    minute = now.minute
    dayofweek = now.weekday()

    print(f"Requested optimization for room: {room_id}")
    print(f"Looking for models: rf_{room_id.upper()}, knn_{room_id.upper()}")
    print(f"Current time features → hour: {hour}, minute: {minute}, dayofweek: {dayofweek}")

    feature_names = ["RelH", "L1", "L2", "Occ", "Act", "Door", "Win"]

    def objective(x, model, comfort_temp, feature_names):
        df = pd.DataFrame([x], columns=feature_names)
        predicted_temp = model.predict(df)[0]
        loss = abs(predicted_temp - comfort_temp)
        print(f"  Trying input: {x} → Predicted Temp: {predicted_temp:.2f}, Target: {comfort_temp:.2f}, Loss: {loss:.4f}")
        return loss

    def optimize_sensor_inputs(knn_model, rf_model, hour, minute, dayofweek, feature_names):
        df_time = pd.DataFrame([{
            "hour": hour,
            "minute": minute,
            "dayofweek": dayofweek
        }])
        comfort_temp = rf_model.predict(df_time)[0]
        print(f"Predicted comfort temperature: {comfort_temp:.2f}")

        bounds = [
            (0, 100),  # RelH
            (0, 100),  # L1
            (0, 100),  # L2
            (0, 1),    # Occ
            (0, 1),    # Act
            (0, 1),    # Door
            (0, 1)     # Win
        ]

        result = differential_evolution(objective, bounds, args=(knn_model, comfort_temp, feature_names), seed=42)

        # Post-process: round categorical values
        optimized = result.x
        optimized[3] = round(optimized[3])  # Occ
        optimized[4] = round(optimized[4])  # Act
        optimized[5] = round(optimized[5])  # Door
        optimized[6] = round(optimized[6])  # Win

        print(f"Optimization success: {result.success}")
        print(f"Optimized input: {optimized}")

        return dict(zip(feature_names, optimized)), comfort_temp

    optimized_sensor, comfort_temp = optimize_sensor_inputs(
        knn_model, rf_model, hour, minute, dayofweek, feature_names
    )

    optimized_sensor["Temp"] = round(comfort_temp, 2)
    print(f"Final optimized sensor package for room {room_id}: {optimized_sensor}")

    return templates.TemplateResponse("_sensors_form.html", {
        "request": request,
        "sensor": optimized_sensor,
        "room_id": room_id
    })