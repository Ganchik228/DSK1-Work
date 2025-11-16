import asyncio
from aiogram import Bot, Dispatcher
from app.handlers.handlers import router
import logging
from app.handlers.keyboards import bot_commands

from dotenv import load_dotenv
import os

load_dotenv()

logging.basicConfig(level=logging.INFO)

dp = Dispatcher()
TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=TOKEN)

async def main() -> None:
    await bot.set_my_commands(bot_commands)
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
