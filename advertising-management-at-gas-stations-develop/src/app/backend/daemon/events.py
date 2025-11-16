import aioping
from fastapi_utilities import repeat_every
from sqlalchemy import select
from database.models import TvTable, async_session
from telegram import Bot
import asyncio

from dotenv import load_dotenv
import os

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


bot = Bot(token=TELEGRAM_TOKEN)

async def send_telegram_message(message: str):
    try:
        await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except Exception as e:
        print(f"Failed to send Telegram message: {e}")

async def check_tv_ping(tv: TvTable) -> bool:
    try:
        await aioping.ping(tv.address, timeout=10)
        return "true"
    except Exception:
        return "false"    

task_lock = asyncio.Lock()

@repeat_every(seconds=10)
async def check_connection():
    if task_lock.locked():
        print("skip")
        return

    async with task_lock:
        try:
            async with async_session() as session:
                result = await session.execute(select(TvTable))
                tvs = result.scalars().all()
                status_changed = False
                
                for tv in tvs:
                    if tv.status == "processing":
                        continue
                        
                    is_connected = await check_tv_ping(tv)
                    
                    if tv.status != is_connected:
                        tv.status = is_connected
                        session.add(tv)
                        status_changed = True
                        print(f"TV {tv.machine_name} status changed to: {'online' if is_connected else 'offline'}")
                        """await send_telegram_message(
                            f"TV {tv.machine_name} status changed to: {'online' if is_connected else 'offline'}"
                        )"""
                
                if status_changed:
                    await session.commit()
                    
        except Exception as e:
            await send_telegram_message(f"Error checking connections: {str(e)}")

