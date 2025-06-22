# app/database/init_db.py
import asyncio
from sqlalchemy import select
from app.database import engine, Base, AsyncSessionLocal
from app.database.models import SensorData, ComfortPreference

seed_rooms = ["A", "B", "C"]

async def init():
    # Step 1: Create tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Step 2: Seed initial data if not already present
    async with AsyncSessionLocal() as session:
        for room in seed_rooms:
            # Check if this room has any sensor data
            result = await session.execute(
                select(SensorData).where(SensorData.room == room)
            )
            exists = result.scalars().first()
            if not exists:
                sensor = SensorData(
                    room=room,
                    Temp=22.0,
                    RelH=40.0,
                    Occ=1,
                    Act=2,
                    Door=0,
                    Win=1,
                )
                preference = ComfortPreference(
                    room=room,
                    temperature=24.0
                )
                session.add_all([sensor, preference])
        await session.commit()

if __name__ == "__main__":
    asyncio.run(init())
