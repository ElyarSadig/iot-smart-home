from app.database import AsyncSessionLocal
from app.database.models import SensorData
from sqlalchemy.future import select
from app.model_registery import model_registry
from datetime import datetime
import pandas as pd

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
                # Define the expected feature names in the same order used in training
                FEATURES = ["RelH", "L1", "L2", "Occ", "Act", "Door", "Win"]

                # Create a DataFrame with feature names to avoid sklearn warning
                df_features = pd.DataFrame([[
                    sensor.RelH,
                    sensor.L1,
                    sensor.L2,
                    sensor.Occ,
                    sensor.Act,
                    sensor.Door,
                    sensor.Win
                ]], columns=FEATURES)

                # Predict and update
                prediction = model.predict(df_features)[0]
                sensor.Temp = round(prediction, 2)
                sensor.created_at = datetime.now()

        await session.commit()