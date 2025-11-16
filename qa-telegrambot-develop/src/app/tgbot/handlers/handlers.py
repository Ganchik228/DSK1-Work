from aiogram import Router, types, F, md
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import httpx
import logging
from openai import OpenAI
from dotenv import load_dotenv

import json

from typing import Union
from urllib.parse import quote

import os
from .keyboards import (
    get_main_menu,
    get_contexts_keyboard,
    get_miniapp_keyboard,
    get_phone_request_keyboard,
)

load_dotenv()
BASE_URL = (os.getenv("BASE_URL") or "").rstrip("/") + "/"
API_KEY = os.getenv("DEEPSEEK_API")

router = Router()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")


class UserState(StatesGroup):
    selected_context = State()
    waiting_for_question = State()
    waiting_for_activation = State()
    waiting_for_phone = State()


async def ensure_user_activated(
    event: Union[types.Message, types.CallbackQuery],
    state: FSMContext,
) -> bool:
    current_state = await state.get_state()
    if current_state == UserState.waiting_for_phone:
        warning = "Поделитесь номером телефона, чтобы продолжить."
        if isinstance(event, types.CallbackQuery):
            await event.answer(warning, show_alert=True)
        else:
            await event.answer(
                warning,
                reply_markup=get_phone_request_keyboard(),
            )
        return False
    if current_state == UserState.waiting_for_activation:
        warning = "Подтвердите пользовательское соглашение, чтобы продолжить."
        if isinstance(event, types.CallbackQuery):
            await event.answer(warning, show_alert=True)
        else:
            await event.answer(warning)
        return False
    return True


@router.message(CommandStart())
async def cmd_start(msg: types.Message, state: FSMContext) -> None:
    user_id = str(msg.from_user.id)
    user_name = str(msg.from_user.full_name)

    data = {"user_id": user_id, "user_name": user_name}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(f"{BASE_URL}user/", json=data)
            response.raise_for_status()
            user_info = response.json()
    except httpx.HTTPError as e:
        logger.error(f"Ошибка при обращении к API: {e}")
        await msg.answer("Ошибка соединения с сервером. Попробуйте позже.")
        return

    user_payload = user_info.get("user", {})

    phone_number = user_payload.get("phone_number")
    is_activated = user_payload.get("is_activated", False)

    if not phone_number:
        await state.set_state(UserState.waiting_for_phone)
        await msg.answer(
            f"Здравствуйте, {md.bold(msg.from_user.full_name)}!\n"
            "Для доступа к боту необходимо поделиться номером телефона.",
            reply_markup=get_phone_request_keyboard(),
        )
        return

    if not is_activated:
        await state.set_state(UserState.waiting_for_activation)
        await msg.answer(
            f"Здравствуйте, {md.bold(msg.from_user.full_name)}!\n"
            "Для продолжения необходимо подтвердить пользовательское соглашение 👇",
            reply_markup=get_miniapp_keyboard(user_id=user_id),
        )
        return

    await state.clear()
    await msg.answer(
        f"Здравствуйте, {md.bold(msg.from_user.full_name)}.",
        reply_markup=get_main_menu(),
    )


@router.message(F.web_app_data)
async def handle_web_app(msg: types.Message, state: FSMContext):
    try:
        data = msg.web_app_data.data
        logger.info(f"📩 Получены данные от MiniApp: {data}")

        payload = json.loads(data)
        user_id = payload.get("user_id")
        action = payload.get("action")

        if not user_id:
            await msg.answer(
                "Не удалось определить пользователя. Откройте форму ещё раз."
            )
            return

        user_id = str(user_id)

        if action == "accept_agreement":
            async with httpx.AsyncClient() as client:
                resp = await client.patch(f"{BASE_URL}user/activate/{user_id}")
                resp.raise_for_status()

            await state.clear()

            await msg.answer(
                "✅ Соглашение подтверждено! Теперь вы можете пользоваться ботом.",
                reply_markup=get_main_menu(),
            )

        elif action == "decline_agreement":
            await state.set_state(UserState.waiting_for_activation)
            await msg.answer(
                "❌ Вы отклонили соглашение. Доступ к функциям бота ограничен.",
                reply_markup=get_miniapp_keyboard(user_id=user_id),
            )
        else:
            await msg.answer("⚠ Неизвестное действие от MiniApp.")

    except Exception as e:
        logger.error(f"Ошибка при обработке web_app_data: {e}")
        await msg.answer("Произошла ошибка при обработке данных. Попробуйте позже.")


@router.message(Command("current_context"))
async def current_context(msg: types.Message, state: FSMContext) -> None:
    if not await ensure_user_activated(msg, state):
        return

    data = await state.get_data()
    if "selected_context" not in data:
        await msg.answer("Тема не выбрана")
    else:
        async with httpx.AsyncClient() as client:
            response = await client.get(url=f"{BASE_URL}context/all")
            contexts = response.json()["contexts"]
            current = next(
                (c for c in contexts if c["data"] == data["selected_context"]), None
            )

        if current:
            await msg.answer(f"Текущая тема: {current['name']}")
        else:
            await msg.answer("Не удалось определить текущую тему")


@router.message(F.text == "Выбрать тему вопроса")
async def select_context(msg: types.Message, state: FSMContext) -> None:
    if not await ensure_user_activated(msg, state):
        return

    current_state = await state.get_state()
    if current_state == UserState.waiting_for_question:
        await msg.answer("Сначала завершите текущий диалог, чтобы выбрать новую тему.")
        return

    async with httpx.AsyncClient() as client:
        response = await client.get(url=f"{BASE_URL}context/all")
        contexts = response.json()["contexts"]

    if not contexts:
        await msg.answer("Нет доступных тем")
        return

    await state.update_data(all_contexts=contexts)
    await msg.answer("Выберите тему:", reply_markup=get_contexts_keyboard(contexts))


@router.callback_query(F.data.startswith("context_"))
async def set_context(callback: types.CallbackQuery, state: FSMContext) -> None:
    if not await ensure_user_activated(callback, state):
        return

    data = await state.get_data()

    if callback.data == "context_cancel":
        await state.update_data(selected_context=None)
        await callback.message.answer("Тема сброшена.", reply_markup=get_main_menu())
    elif callback.data.startswith("context_page_"):
        page = int(callback.data.split("_")[2])
        contexts = data.get("all_contexts", [])
        await callback.message.edit_reply_markup(
            reply_markup=get_contexts_keyboard(contexts, page=page)
        )
    else:
        context_id = callback.data.split("_")[1]
        async with httpx.AsyncClient() as client:
            response = await client.get(url=f"{BASE_URL}context/{context_id}")
            context_data = response.json()["context_data"]

        await state.update_data(
            selected_context=context_data["contextData"],
            current_context_name=context_data["contextName"],
        )
        await state.set_state(UserState.waiting_for_question)
        await callback.message.answer(
            f"Текущая тема: {context_data['contextName']}\n"
            f"Теперь вы можете сразу задать вопрос по этой теме.",
            reply_markup=get_main_menu(in_chat=True),
        )
    await callback.answer()


@router.message(F.text == "❌ Завершить диалог")
async def end_chat(msg: types.Message, state: FSMContext) -> None:
    if not await ensure_user_activated(msg, state):
        return

    await state.set_state(None)
    await state.update_data(conversation_history=[])
    await msg.answer(
        "Диалог завершен. Вы можете начать новый диалог в любое время.",
        reply_markup=get_main_menu(),
    )


@router.message(F.text == "Задать вопрос")
async def ask_question(msg: types.Message, state: FSMContext) -> None:
    if not await ensure_user_activated(msg, state):
        return

    current_state = await state.get_state()
    if current_state == UserState.waiting_for_question:
        await msg.answer(
            "Вы уже в режиме диалога. Введите ваш вопрос или завершите текущий диалог."
        )
        return

    data = await state.get_data()
    if "selected_context" not in data or data["selected_context"] is None:
        await msg.answer(
            "Для начала выберите тему из меню.\n"
            "Нажмите кнопку 'Выбрать тему вопроса' и укажите нужную тематику.",
            reply_markup=get_main_menu(),
        )
        return

    current_context_name = data.get("current_context_name", "Не выбрана")
    await msg.answer(
        f"Текущая тема: {current_context_name}\nВведите ваш вопрос по выбранной тематике:",
        reply_markup=get_main_menu(in_chat=True),
    )
    await state.set_state(UserState.waiting_for_question)


@router.message(UserState.waiting_for_question)
async def process_question(msg: types.Message, state: FSMContext) -> None:
    if not await ensure_user_activated(msg, state):
        return
    try:
        data = await state.get_data()
        await msg.answer("Ваш вопрос обрабатывается, пожалуйста подождите...")

        conversation_history = data.get("conversation_history", [])

        if not conversation_history:
            conversation_history.append(
                {
                    "role": "system",
                    "content": f"Ты помощник в компании отвечающий на вопросы. Не отвечай на вопросы не по теме. Если в теме указаны ссылки предоставь их. Отвечай максимально кратко. Ответ давай в обычном тексте без markdown форматирования.\n Тема вопроса:\n{data['selected_context']}",
                }
            )

        conversation_history.append({"role": "user", "content": msg.text})

        logger.info("Отправка запроса в Deepseek:")
        logger.info(f"Контекст: {data['selected_context']}")
        logger.info(f"Вопрос: {msg.text}")
        logger.info(f"История диалога: {conversation_history}")

        response = client.chat.completions.create(
            model="deepseek-chat", messages=conversation_history
        )

        answer = response.choices[0].message.content
        conversation_history.append({"role": "assistant", "content": answer})
        await state.update_data(conversation_history=conversation_history)

        await msg.answer(answer, reply_markup=get_main_menu(in_chat=True), parse_mode=None)
        
        json = {
            "user_id": f"{msg.from_user.id}",
            "request": f"{msg.text}",
            "response": f"{answer}",
            "date": f"{msg.date.isoformat()}",
        }

        async with httpx.AsyncClient() as cl:
            response = await cl.post(url=f"{BASE_URL}message/", json=json)

    except Exception as e:
        logger.error(f"Error processing question: {e}")
        await msg.answer(
            "Произошла ошибка при обработке вопроса. Попробуйте позже.",
            reply_markup=get_main_menu(in_chat=True),
        )


@router.message(UserState.waiting_for_phone, F.contact)
async def handle_phone_contact(msg: types.Message, state: FSMContext) -> None:
    contact = msg.contact
    if not contact or contact.user_id != msg.from_user.id:
        await msg.answer(
            "Нужно поделиться только собственным номером телефона.",
            reply_markup=get_phone_request_keyboard(),
        )
        return

    phone_number = contact.phone_number
    user_id = str(msg.from_user.id)

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            encoded_phone = quote(phone_number, safe="")
            resp = await client.patch(f"{BASE_URL}user/{user_id}/phone/{encoded_phone}")
            resp.raise_for_status()
    except httpx.HTTPError as e:
        logger.error(f"Ошибка при сохранении телефона: {e}")
        await msg.answer(
            "Не удалось сохранить номер телефона. Попробуйте позже.",
            reply_markup=get_phone_request_keyboard(),
        )
        return

    await state.set_state(UserState.waiting_for_activation)
    await msg.answer(
        "✅ Номер телефона сохранён.\n"
        "Теперь подтвердите пользовательское соглашение, чтобы получить доступ.",
        reply_markup=get_miniapp_keyboard(user_id=user_id),
    )


@router.message(UserState.waiting_for_phone)
async def remind_phone(msg: types.Message, state: FSMContext) -> None:
    await msg.answer(
        "Пожалуйста, поделитесь номером телефона с помощью кнопки ниже.",
        reply_markup=get_phone_request_keyboard(),
    )


@router.message(Command("give_phone"))
async def give_phone_command(msg: types.Message, state: FSMContext) -> None:
    await state.set_state(UserState.waiting_for_phone)
    await msg.answer(
        "Отправьте свой номер телефона через кнопку ниже.",
        reply_markup=get_phone_request_keyboard(),
    )
