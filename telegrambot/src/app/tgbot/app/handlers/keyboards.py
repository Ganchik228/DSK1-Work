from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, BotCommand
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from app.database.db_funcs import get_roles


bot_commands = [
    BotCommand(command="/start", description="Начать"),
]

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Оставить отзыв")],
        [KeyboardButton(text="Изменить роль")],
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
)

async def reply_roles():
    keyboard = ReplyKeyboardBuilder()
    roles = await get_roles()
    for role in roles:
        keyboard.add(KeyboardButton(text=role))
    return keyboard.adjust(3).as_markup(resize_keyboard=True, one_time_keyboard=True)


async def reply_contacts():
    keyboard = ReplyKeyboardBuilder()
    keyboard.add(KeyboardButton(text="Поделиться контактами", request_contact=True))
    keyboard.add(KeyboardButton(text="Пропустить"))
    return keyboard.adjust(1).as_markup(resize_keyboard=True, one_time_keyboard=True)
