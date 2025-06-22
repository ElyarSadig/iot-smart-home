from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from app.routers import home, room
from app.model_registery import load_models
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.tasks import update_all_predictions, retrain_comfort_models

load_models()

scheduler = AsyncIOScheduler()
scheduler.add_job(update_all_predictions, 'interval', seconds=5)  # every 5s
scheduler.add_job(retrain_comfort_models, 'interval', seconds=10)  # every 5s
scheduler.start()

app = FastAPI()

templates = Jinja2Templates(directory="app/templates")

app.include_router(home.router)
app.include_router(room.router)
