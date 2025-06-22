import os
import pandas as pd
import joblib
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer

from sqlalchemy.future import select
from app.database import AsyncSessionLocal
from app.database.models import ComfortPreference, SensorData
from app.model_registery import model_registry

DATA_DIR = "data/room_comfort_temperature/rooms"
MODEL_DIR = "models"
FEATURES = ["RelH", "L1", "L2", "Occ", "Act", "Door", "Win"]
TARGET = "Temp"
ROOMS = ["A", "B", "C"]

async def update_all_predictions():
    async with AsyncSessionLocal() as session:
        for room_id, model in model_registry.items():
            result = await session.execute(
                select(SensorData)
                .where(SensorData.room == room_id)
                .order_by(SensorData.created_at.desc())
                .limit(1)
            )
            sensor = result.scalar_one_or_none()

            if sensor:
                FEATURES = ["RelH", "L1", "L2", "Occ", "Act", "Door", "Win"]
                df_features = pd.DataFrame([[
                    sensor.RelH,
                    sensor.L1,
                    sensor.L2,
                    sensor.Occ,
                    sensor.Act,
                    sensor.Door,
                    sensor.Win
                ]], columns=FEATURES)

                prediction = model.predict(df_features)[0]
                sensor.Temp = round(prediction, 2)
                sensor.created_at = datetime.now()

        await session.commit()

async def fetch_comfort_data_from_db(room_id: str) -> pd.DataFrame:
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(ComfortPreference).where(ComfortPreference.room == room_id)
        )
        records = result.scalars().all()

        if not records:
            return pd.DataFrame()

        return pd.DataFrame([{
            "temperature": r.temperature,
            "created_at": r.created_at
        } for r in records])

async def retrain_comfort_models():
    for room in ROOMS:
        print(f"Retraining comfort model for Room {room}")

        # Load from CSV (existing base dataset)
        csv_path = os.path.join(DATA_DIR, f"room_{room}.csv")
        if os.path.exists(csv_path):
            csv_df = pd.read_csv(csv_path, parse_dates=["created_at"])
        else:
            csv_df = pd.DataFrame()

        # Load from DB (recent feedback)
        db_df = await fetch_comfort_data_from_db(room)

        # Merge datasets
        full_df = pd.concat([csv_df, db_df], ignore_index=True)
        if full_df.empty:
            print(f"No data available for room {room}. Skipping.")
            continue

        full_df = full_df.dropna(subset=["temperature", "created_at"])
        full_df['hour'] = full_df['created_at'].dt.hour
        full_df['minute'] = full_df['created_at'].dt.minute
        full_df['dayofweek'] = full_df['created_at'].dt.dayofweek

        X = full_df[["hour", "minute", "dayofweek"]]
        y = full_df["temperature"]

        # Train model
        pipeline = Pipeline([
            ("preprocessor", ColumnTransformer([
                ("num", "passthrough", ["hour", "minute", "dayofweek"])
            ])),
            ("regressor", RandomForestRegressor(n_estimators=100, random_state=42))
        ])

        pipeline.fit(X, y)

        model_path = os.path.join(MODEL_DIR, f"random_forest_model_room_{room}.pkl")
        joblib.dump(pipeline, model_path)
        model_registry[f"rf_{room}"] = pipeline

        print(f"Updated comfort model saved and registered for Room {room}")