import asyncio
from aiogram import Bot, Dispatcher
from handlers.handlers import router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand

from dotenv import load_dotenv

import logging
import os

load_dotenv()

logging.basicConfig(level=logging.INFO)

dp = Dispatcher()
TOKEN = os.getenv("TG_TOKEN")
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN))


async def setup_commands(bot: Bot):
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Запустить бота"),
        ]
    )


async def main() -> None:
    dp.include_router(router)
    await setup_commands(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
