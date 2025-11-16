from fastapi import FastAPI, Request
import uvicorn

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

import logging
from contextlib import asynccontextmanager

from models import init_db
from utilities.daemon import update_nomenclature
from api1c.router import router as router_1c

import time

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up")
    await init_db()
    scheduler = AsyncIOScheduler()
    trigger = CronTrigger(hour=3, minute=0,timezone='Asia/Yekaterinburg')
    scheduler.add_job(update_nomenclature, trigger=trigger)
    scheduler.start()
    logger.info("Scheduler started")
    yield
    scheduler.shutdown()
    logger.info("Shutting down")

app = FastAPI(lifespan=lifespan)

@app.middleware("http")
async def counter(req: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(req)
    process_time = time.perf_counter() - start_time
    print(f"⏱ {req.method} {req.url.path} - {process_time:.4f} sec")
    return response

app.include_router(router_1c)

@app.get("/")
async def root():
    return {"status":"ok"}

if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=25565)
