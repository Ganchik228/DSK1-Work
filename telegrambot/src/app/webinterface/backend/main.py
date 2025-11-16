from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from contextlib import asynccontextmanager

import uvicorn

from models.db_model import init_db
from routers import web_router, auth_router

@asynccontextmanager
async def lifespan(app:FastAPI):
    print("starting up")
    await init_db()
    yield
    print("shutting down")

app = FastAPI(lifespan=lifespan)

app.include_router(web_router)
app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return {"message": "Root"}

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_level="debug",
        reload=True
    )
