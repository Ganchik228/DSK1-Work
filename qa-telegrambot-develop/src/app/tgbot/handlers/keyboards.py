from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardButton,
    WebAppInfo,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = (os.getenv("BASE_URL") or "").rstrip("/") + "/"


def get_phone_request_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="📞 Поделиться номером телефона", request_contact=True
                )
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def get_main_menu(in_chat=False):
    if in_chat:
        return ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="❌ Завершить диалог")]],
            resize_keyboard=True,
            one_time_keyboard=True,
        )
    else:
        return ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="Задать вопрос")],
                [KeyboardButton(text="Выбрать тему вопроса")],
            ],
            resize_keyboard=True,
            one_time_keyboard=True,
        )


def get_miniapp_keyboard(user_id: str | int | None = None):
    url = f"{BASE_URL}miniapp/{user_id}"

    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="📄 Подтвердить пользовательское соглашение",
                    web_app=WebAppInfo(url=url),
                )
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def get_contexts_keyboard(contexts, page=0, page_size=4):
    builder = InlineKeyboardBuilder()

    total_pages = (len(contexts) + page_size - 1) // page_size
    start_idx = page * page_size
    end_idx = start_idx + page_size

    for context in contexts[start_idx:end_idx]:
        builder.add(
            InlineKeyboardButton(
                text=context["name"], callback_data=f"context_{context['id']}"
            )
        )

    nav_buttons = []
    if page > 0:
        nav_buttons.append(
            InlineKeyboardButton(
                text="⬅️ Назад", callback_data=f"context_page_{page - 1}"
            )
        )
    if page < total_pages - 1:
        nav_buttons.append(
            InlineKeyboardButton(
                text="Вперед ➡️", callback_data=f"context_page_{page + 1}"
            )
        )

    if nav_buttons:
        builder.row(*nav_buttons)

    builder.add(
        InlineKeyboardButton(text="❌ Отменить", callback_data="context_cancel")
    )

    builder.adjust(1)
    return builder.as_markup()
