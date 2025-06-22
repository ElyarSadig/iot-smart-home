import asyncio
from sqlalchemy import select
from app.database import engine, Base, AsyncSessionLocal
from app.database.models import SensorData, ComfortPreference, RoomPreference

seed_rooms = ["A", "B", "C"]

async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as session:
        for room in seed_rooms:
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
                    L1=500,
                    L2=450,
                )
                preference = ComfortPreference(
                    room=room,
                    temperature=24.0
                )
                room_preference = RoomPreference(
                    room=room,
                    temperature=25
                )
                session.add_all([sensor, preference, room_preference])
        await session.commit()

if __name__ == "__main__":
    asyncio.run(init())
