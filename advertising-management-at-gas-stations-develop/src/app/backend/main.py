from fastapi import FastAPI, File, UploadFile, Form, Request, Depends, BackgroundTasks, Body, Response
from fastapi.responses import JSONResponse, HTMLResponse, StreamingResponse
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import httpx


from moviepy import *
from moviepy.video.io.ffmpeg_writer import FFMPEG_VideoWriter


import json
import logging
from pathlib import Path
import asyncio
import aiofiles
from telegram import Bot
import shutil
import hashlib
import tempfile

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
import re
import time

from database.models import TvTable, get_db, Categories
from daemon.events import check_connection
from routers import auth_router, admin_router

from PIL import Image
import io

from dotenv import load_dotenv
import os

load_dotenv()



TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
SSH_PORT = 33322
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
COMMON_DIR = UPLOAD_DIR / "common"
COMMON_DIR.mkdir(parents=True, exist_ok=True)
REDACTED_DIR = UPLOAD_DIR / "redacted"
REDACTED_DIR.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up")
    await check_connection()
    yield
    print("Shutting down")

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://10.99.10.55:5173", "http://10.99.10.55:3000",
                   "http://10.99.11.230:5173", "http://10.99.11.230:3000", "http://172.20.21.49:5173",
                   "http://176.109.102.60:5173", "http://176.109.102.60:3000", "http://192.168.110.101:5173",
                   "http://192.168.110.101:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(admin_router)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

@app.middleware("http")
async def custom_access_log(request: Request, call_next):
    start_time = time.time()
    try:
        response: Response = await call_next(request)
    except Exception as e:
        logger.error(
            f"{request.method} {request.url.path} {request.url.query} "
            f"from {request.client.host} -> 500 INTERNAL SERVER ERROR | Exception: {e}"
        )
        raise

    process_time = (time.time() - start_time) * 1000
    if not re.match(r"^/sse", request.url.path):
        logger.info(
            f"{request.method} {request.url.path} {request.url.query} "
            f"from {request.client.host} -> {response.status_code} | {process_time:.2f}ms"
        )
    return response

bot = Bot(token=TELEGRAM_TOKEN)

async def rsync_command(source: str, target: TvTable, delete: bool = False):
    remote_path = f"/home/{target.user_name}/Videos/"
    password = target.password
    cmd = [
        "sshpass", "-p", password,
        "rsync",
        "-avz",
        "--progress",
        "--rsh", f"ssh -p {SSH_PORT} -o StrictHostKeyChecking=no",
        source,
        f"{target.user_name}@{target.address}:{remote_path}"
    ]
    if delete:
        cmd.append("--delete")
    logger.info(f"Running rsync command: {' '.join(cmd)}")
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        error_msg = stderr.decode().strip()
        logger.error(f"rsync error: {error_msg}")
        raise RuntimeError(f"rsync error: {error_msg}")
    logger.info(f"rsync completed successfully for {target.machine_name}")

async def sync_tv_directory(target: TvTable, delete: bool = False):
    local_dir = UPLOAD_DIR / target.machine_name
    await rsync_command(f"{local_dir}/", target, delete=delete)

async def send_telegram_message(message: str):
    try:
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")

async def restart_machine(target: TvTable):
    try:
        password = target.password
        proc = await asyncio.create_subprocess_exec(
            "sshpass", "-p", password,
            "ssh",
            "-p", str(SSH_PORT),
            "-o", "StrictHostKeyChecking=no",
            f"{target.user_name}@{target.address}",
            "sudo reboot",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()
        if proc.returncode != 0:
            error_msg = stderr.decode().strip()
            logger.error(f"Error restarting {target.machine_name}: {error_msg}")
            raise RuntimeError(f"Error restarting {target.machine_name}: {error_msg}")
        logger.info(f"Successfully restarted {target.machine_name}")
    except Exception as e:
        logger.error(f"Error restarting {target.machine_name}: {e}")
        await send_telegram_message(f"Error restarting {target.machine_name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

async def async_resize_video(input_file: Path, output_file: Path):
    def check_resolution(path: Path):
        with VideoFileClip(str(path)) as clip:
            return clip.w, clip.h
    width, height = await asyncio.to_thread(check_resolution, input_file)
    if width == 1920 and height == 1080:
        shutil.copy2(input_file, output_file)
        return
    
    cmd = [
        "HandBrakeCLI",
        "-i", str(input_file),
        "-o", str(output_file),
        "--width", "1920",
        "--height", "1080"
    ]
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()
    if proc.returncode != 0:
        raise RuntimeError(f"HandBrakeCLI error: {stderr.decode().strip()}")

def generate_playlist(target: TvTable):
    local_dir = UPLOAD_DIR / target.machine_name
    playlist_path = local_dir / "playlist.m3u"
    with open(playlist_path, "w") as f:
        f.write("#EXTM3U\n")
        for filename in target.videos:
            f.write(f"{filename}\n")


@app.get("/")
async def root():
    return {"message": "Hello its root!"}

@app.get("/tvs")
async def get_tvs(category: Optional[str] = "all", db: AsyncSession = Depends(get_db)):
    stmt = select(TvTable, Categories).outerjoin(Categories, TvTable.category_id == Categories.id)
    if category != "all":
        if (category == "unassigned"):
            stmt = stmt.where(TvTable.category_id.is_(None))
        else:
            stmt = stmt.where(TvTable.category_id == int(category))
    try:
        result = await db.execute(stmt)
        rows = result.all()
        tvs = []
        for tv, category_obj in rows:
            tvs.append({
                "id": tv.id,
                "name": tv.machine_name,
                "address": tv.address,
                "videos": tv.videos,
                "status": tv.status,
                "category": category_obj.name if category_obj else None,
            })
        return sorted(tvs, key=lambda x: x["id"])
    except Exception as e:
        await send_telegram_message(f"GET /tvs: Error - {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/tvs/{tv_id}/info")
async def get_tv_info(tv_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TvTable).filter(TvTable.id == tv_id))
    tv = result.scalar_one_or_none()
    if not tv:
        raise HTTPException(status_code=404, detail="TV not found")
    return {
        "id": tv.id,
        "name": tv.machine_name,
        "address": tv.address,
        "videos": tv.videos,
        "status": tv.status,
    }

uploads_in_progress = set()
uploads_lock = asyncio.Lock()

@app.post("/videos")
async def create_video(files: list[UploadFile] = File(...)):
    results = []
    for file in files:
        if not file.filename.lower().endswith((".mp4", ".avi", ".mov", ".webm")):
            results.append({"filename": file.filename, "status": "Неверный тип файла"})
            continue
        if (COMMON_DIR / file.filename).exists():
            results.append({"filename": file.filename, "status": "Файл с таким именем уже существует"})
            continue
        async with uploads_lock:
            if file.filename in uploads_in_progress:
                results.append({"filename": file.filename, "status": "Файл уже загружается"})
                continue
            uploads_in_progress.add(file.filename)
        content = await file.read()
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix, dir=str(UPLOAD_DIR)) as tmp:
            tmp.write(content)
            temp_path = Path(tmp.name)
        processed_path = COMMON_DIR / file.filename
        try:
            await async_resize_video(temp_path, processed_path)
        except Exception as e:
            results.append({"filename": file.filename, "status": f"Ошибка: {e}"})
            temp_path.unlink(missing_ok=True)
            continue
        finally:
            temp_path.unlink(missing_ok=True)
            async with uploads_lock:
                uploads_in_progress.discard(file.filename)
        results.append({"filename": file.filename, "status": "Загружено успешно"})
    return JSONResponse(content={"results": results})

@app.post("/deployments")
async def create_deployment(background_tasks: BackgroundTasks, payload: dict = Body(...), db: AsyncSession = Depends(get_db)):
    target_ids = payload.get("targets", [])
    selected_videos = payload.get("videos", [])
    result = await db.execute(select(TvTable).filter(TvTable.id.in_(target_ids)))
    target_records = result.scalars().all()
    if not target_records:
        raise HTTPException(status_code=404, detail="Нет подходящих целей")
    
    for target in target_records:
        target.status = "processing"
        db.add(target)
        await db.commit()
        
        target_dir = UPLOAD_DIR / target.machine_name
        target_dir.mkdir(parents=True, exist_ok=True)
        for video in selected_videos:
            source = COMMON_DIR / video
            if source.exists():
                await asyncio.to_thread(shutil.copy2, source, target_dir / video)
        new_videos = [f.name for f in target_dir.iterdir() if f.is_file() and f.name.lower().endswith(('.mp4','.avi','.mov','.webm'))]
        target.videos = new_videos
        db.add(target)
        await db.commit()
        generate_playlist(target)
        
        background_tasks.add_task(sync_tv_directory, target)
        background_tasks.add_task(restart_machine, target)
    
    return JSONResponse(content={"message": "Видео отправлены на устройства и устройство перезапущено"})

@app.delete("/videos")
async def delete_videos(background_tasks: BackgroundTasks, payload: dict = Body(...), db: AsyncSession = Depends(get_db)):
    try:
        tv_id = payload.get("tv_id")
        filenames = payload.get("filenames")
        if not tv_id or not filenames:
            raise HTTPException(status_code=400, detail="Missing tv_id or filenames in request body")
        
        result = await db.execute(select(TvTable).filter(TvTable.id == tv_id))
        target = result.scalar_one_or_none()
        if not target:
            raise HTTPException(status_code=404, detail="Target TV not found")
        
        tv_dir = UPLOAD_DIR / target.machine_name
        for filename in filenames:
            file_path = tv_dir / filename
            if file_path.exists():
                file_path.unlink()
        
        remaining_files = [f.name for f in tv_dir.iterdir() if f.is_file() and f.name != "playlist.m3u"]
        target.videos = remaining_files
        target.status = "processing"
        db.add(target)
        await db.commit()
        generate_playlist(target)
        background_tasks.add_task(sync_tv_directory, target, delete=True)
        background_tasks.add_task(restart_machine, target)
        
        return JSONResponse(content={
            "message": f"Successfully deleted {len(filenames)} files",
            "deleted_files": filenames
        })
    except Exception as e:
        await db.rollback()
        await send_telegram_message(f"DELETE /videos: Error - {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/tvs/{tv_id}")
async def update_tv(tv_id: int, request: Request, db: AsyncSession = Depends(get_db)):
    try:
        body = await request.json()
        result = await db.execute(select(TvTable).filter(TvTable.id == tv_id))
        target = result.scalar_one_or_none()
        if not target:
            raise HTTPException(status_code=404, detail="TV not found")
        if "machine_name" in body:
            target.machine_name = body["machine_name"]
        await sync_tv_directory(target, delete=True)
        await restart_machine(target)
        local_dir = UPLOAD_DIR / target.machine_name
        target.videos = [f.name for f in local_dir.iterdir() if f.is_file() and f.name !="playlist.m3u"]
        target.status = "processing"
        db.add(target)
        await db.commit()
        return JSONResponse(content={"message": "Sync completed successfully"})
    except Exception as e:
        await send_telegram_message(f"PATCH /tvs/{tv_id}: Error - {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/tvs/{tv_id}/restart")
async def restart_tv(tv_id: int, db: AsyncSession = Depends(get_db)):
    try:
        result = await db.execute(select(TvTable).filter(TvTable.id == tv_id))
        target = result.scalar_one_or_none()
        if not target:
            raise HTTPException(status_code=404, detail="TV not found")
        await restart_machine(target)
        target.status = "processing"
        db.add(target)
        await db.commit()
        return JSONResponse(content={"message": "Machine restarted successfully"})
    except Exception as e:
        await send_telegram_message(f"POST /tvs/{tv_id}/restart: Error - {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/new_tv_init")
async def init_tv(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        data = await request.json()
        machine_name = data.get("machine_name")
        address = data.get("address")
        username = data.get("user_name")
        password = data.get("password")
        result = await db.execute(
            select(TvTable).filter(TvTable.machine_name == machine_name)
        )
        existing_tv = result.scalar_one_or_none()
        if existing_tv:
            existing_tv.address = address
            existing_tv.status = "True"
            db.add(existing_tv)
            await db.commit()
            tv_upload_dir = UPLOAD_DIR / machine_name
            tv_upload_dir.mkdir(parents=True, exist_ok=True)
            message = f"""POST /new_tv_init: TV data updated
            Request: {data},
            Name: {machine_name},
            IP: {address},
            pswd: {password}
            """
        else:
            new_entry = TvTable(
                machine_name=machine_name,
                address=address,
                videos=[],
                password=password,
                user_name=username,
                status="True"
            )
            db.add(new_entry)
            await db.commit()
            tv_upload_dir = UPLOAD_DIR / machine_name
            tv_upload_dir.mkdir(parents=True, exist_ok=True)
            message = f"""POST /new_tv_init: New TV added
            Request: {data},
            Name: {machine_name},
            IP: {address},
            pswd: {password}
            """
        await send_telegram_message(message)
        return {"status": "ok", "message": message}
    except Exception as e:
        await db.rollback()
        await send_telegram_message(f"POST /new_tv_init: Error - {str(e)}")
        return JSONResponse(content={"status": "error", "message": str(e)},
                            status_code=500)

@app.get("/categories")
async def get_categories(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Categories))
    cats = result.scalars().all()
    return [{"id": cat.id, "name": cat.name} for cat in cats]

@app.post("/categories")
async def create_category(payload: dict = Body(...), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Categories).filter(Categories.name == payload["name"]))
    existing_cat = result.scalar_one_or_none()
    if existing_cat:
        raise HTTPException(status_code=400, detail="Категория уже существует")
    new_cat = Categories(name=payload["name"])
    db.add(new_cat)
    await db.commit()
    await db.refresh(new_cat)
    return {"id": new_cat.id, "name": new_cat.name}

@app.put("/categories/{cat_id}")
async def update_category(cat_id: int, payload: dict = Body(...), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Categories).filter(Categories.id == cat_id))
    cat = result.scalar_one_or_none()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    cat.name = payload["name"]
    db.add(cat)
    await db.commit()
    return {"id": cat.id, "name": cat.name}

@app.delete("/categories/{cat_id}")
async def delete_category(cat_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Categories).filter(Categories.id == cat_id))
    cat = result.scalar_one_or_none()
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found")
    await db.delete(cat)
    await db.commit()
    return {"message": "Category deleted"}

@app.put("/tvs/{tv_id}/category")
async def assign_tv_category(tv_id: int, payload: dict = Body(...), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TvTable).filter(TvTable.id == tv_id))
    tv = result.scalar_one_or_none()
    if not tv:
        raise HTTPException(status_code=404, detail="TV not found")
    tv.category_id = payload.get("category_id")
    db.add(tv)
    await db.commit()
    return {
        "id": tv.id,
        "name": tv.machine_name,
        "address": tv.address,
        "videos": tv.videos,
        "status": tv.status,
        "category_id": tv.category_id
    }

@app.put("/tvs/{tv_id}/videos")
async def update_videos_order(tv_id: int, payload: dict = Body(...), db: AsyncSession = Depends(get_db)):
    try:
        new_order = payload.get("videos")
        if not isinstance(new_order, list):
            raise HTTPException(status_code=400, detail="Поле videos должно быть списком")
        result = await db.execute(select(TvTable).filter(TvTable.id == tv_id))
        tv = result.scalar_one_or_none()
        if not tv:
            raise HTTPException(status_code=404, detail="TV не найден")
        tv.videos = new_order
        tv.status = "processing"
        db.add(tv)
        await db.commit()
        generate_playlist(tv)
        await sync_tv_directory(tv)
        await restart_machine(tv)
        return {"message": "Порядок роликов обновлен"}
    except Exception as e:
        return {"message": "Изменить порядок не удалось"}

@app.get("/sse/tv_status/{tv_id}")
async def tv_status_sse(tv_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(TvTable).filter(TvTable.id == tv_id))
    tv = result.scalar_one_or_none()
    if not tv:
        raise HTTPException(status_code=404, detail="TV not found")
    
    url = f"http://{tv.address}:8080/requests/status.json"
    
    async def event_generator():
        async with httpx.AsyncClient(timeout=5) as client:
            while True:
                try:
                    resp = await client.get(url, auth=httpx.BasicAuth("", "123321"))
                    resp.raise_for_status()
                    status_data = resp.json()
                    current_video = (
                        status_data.get("information", {})
                                   .get("category", {})
                                   .get("meta", {})
                    )
                    current_video["position"] = status_data.get("position", 0)
                    yield f"data: {json.dumps(current_video)}\n\n"
                except Exception as e:
                    error_data = {"error": f"Error fetching status: {e}"}
                    yield f"data: {json.dumps(error_data)}\n\n"
                    break
                await asyncio.sleep(0.5)    
    
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/sse/tvs_db_status")
async def tvs_db_status_sse(db: AsyncSession = Depends(get_db)):
    async def event_generator():
        while True:
            try:
                result = await db.execute(select(TvTable.id, TvTable.status))
                tvs = [{"id": row.id, "status": row.status} for row in result.fetchall()]
                yield f"data: {json.dumps(tvs)}\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e)})}\n\n"
                break
            await asyncio.sleep(0.5)
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@app.get("/videos")
async def get_videos():
    common_dir = UPLOAD_DIR / "common"
    videos = [f.name for f in common_dir.iterdir() if f.is_file() and f.name.lower().endswith(('.mp4', '.avi', '.mov', '.webm'))]
    return JSONResponse(content={"videos": videos})

@app.get("/videos/preview/{video_name}")
async def video_preview(video_name: str):
    common_dir = UPLOAD_DIR / "common"
    video_path = common_dir / video_name
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Видео не найдено")
    try:
        with VideoFileClip(str(video_path)) as clip:
            t = 1 if clip.duration > 1 else clip.duration / 2
            frame = clip.get_frame(t)
        image = Image.fromarray(frame.astype("uint8"), "RGB")
        buffer = io.BytesIO()
        image.save(buffer, format="JPEG")
        buffer.seek(0)
        return StreamingResponse(buffer, media_type="image/jpeg")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/videos/common")
async def delete_common_videos(filenames: List[str] = Form(...)):
    common_dir = UPLOAD_DIR / "common"
    deleted = []
    not_found = []
    for fname in filenames:
        file_path = common_dir / fname
        if file_path.exists():
            file_path.unlink()
            deleted.append(fname)
        else:
            not_found.append(fname)
    return JSONResponse(content={
        "message": f"Удалено: {len(deleted)} файлов",
        "deleted_files": deleted,
        "not_found": not_found
    })

if __name__ == "__main__":
    uvicorn.run(
        'main:app', 
        host="0.0.0.0", 
        port=8000, 
        access_log=False,
        log_config=None,
        reload=True
    )
