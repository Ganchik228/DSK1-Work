from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn

from contextlib import asynccontextmanager
from models.db import init_db
from routers.user_router import router as user_router
from routers.context_router import router as context_router
from routers.message_router import router as message_router
from routers.auth_router import router as auth_router
from routers.miniapp_router import router as miniapp_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up")
    await init_db()
    yield
    print("Shutting down")


app = FastAPI(lifespan=lifespan, openapi_prefix="/api")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(user_router)
app.include_router(context_router)
app.include_router(message_router)
app.include_router(auth_router)
app.include_router(miniapp_router)


@app.get("/")
async def root():
    return {"message": "Root"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, log_level="debug", reload=True)
