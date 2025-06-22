import asyncio
from . import engine, Base
import app.database.models  # ensure models are loaded

async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

if __name__ == "__main__":
    asyncio.run(init())
