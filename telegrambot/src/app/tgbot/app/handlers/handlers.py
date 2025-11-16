from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.utils.markdown import hbold
from aiogram.types import ReplyKeyboardRemove

import app.handlers.keyboards as kb
import app.database.db_funcs as dbf

router = Router()


class ReviewStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_role = State()
    waiting_for_review = State()
    waiting_for_contacts = State()
    main_menu = State()




@router.message(CommandStart())
async def cmd_start(msg: types.Message, state: FSMContext) -> None:
    user = await dbf.set_user(chat_id=msg.from_user.id, name=None)
    if user:
        await state.update_data(name=user)
        await state.set_state(ReviewStates.main_menu)
        await show_main_menu(msg, state)
    else:
        reply_text = f"""
        👋 Здравствуйте!\nВы попали в бот обратной связи с генеральным директором компании «ДСК-1» Токмаджаном Богданом Валерьевичем.\nПожалуйста, оставьте отзыв или вопрос.\nЧтобы начать введите имя:
        """
        await msg.answer(
            text=reply_text,
            parse_mode='HTML',
        )
        await state.set_state(ReviewStates.waiting_for_name)


@router.message(ReviewStates.waiting_for_name)
async def get_name(msg: types.Message, state: FSMContext) -> None:
    user_name = msg.text
    await dbf.set_user(chat_id=msg.from_user.id, name=user_name)
    await state.update_data(name=user_name)

    reply_text = f"Спасибо, {hbold(user_name)}! Теперь выберите кто вы:"
    await msg.answer(
        text=reply_text,
        parse_mode='HTML',
        reply_markup=await kb.reply_roles()
    )
    await state.set_state(ReviewStates.waiting_for_role)


@router.message(ReviewStates.waiting_for_role)
async def get_role(msg: types.Message, state: FSMContext) -> None:
    user_role = msg.text
    await state.update_data(role=user_role)

    reply_text = f"Оставьте, пожалуйста, обратную связь:"
    await msg.answer(
        text=reply_text,
        parse_mode='HTML',
    )
    await state.set_state(ReviewStates.waiting_for_review)


@router.message(ReviewStates.waiting_for_review)
async def get_review(msg: types.Message, state: FSMContext) -> None:
    user_review = msg.text
    user_data = await state.get_data()
    await state.update_data(review=user_review)
    await dbf.set_review(
        message_text=user_review,
        chat_id=msg.from_user.id,
        role_name=user_data.get('role'),
        date=msg.date
    )
    existing_phone = await dbf.get_contact(msg.from_user.id)
    if existing_phone:
        reply_text = f"Спасибо за обратную связь!"
        await msg.answer(
            text=reply_text,
            parse_mode='HTML',
            reply_markup=ReplyKeyboardRemove(),
        )
        await state.set_state(ReviewStates.main_menu)
        await show_main_menu(msg, state)
    else:
        reply_text = f"""Спасибо за обратную связь!\n📞Хотите, чтобы с вами связались?"""
        await msg.answer(
            text=reply_text,
            parse_mode='HTML',
            reply_markup=await kb.reply_contacts(),
        )
        await state.set_state(ReviewStates.waiting_for_contacts)


async def show_main_menu(msg: types.Message, state: FSMContext) -> None:
    user_data = await state.get_data()
    user_name = user_data.get('name', 'пользователь')
    reply_text = f"""
    👋 Здравствуйте, {hbold(user_name)}!\nВы попали в бот обратной связи с генеральным директором компании «ДСК-1» Токмаджаном Богданом Валерьевичем.\nПожалуйста, оставьте отзыв или вопрос!"""
    await msg.answer(
        text=reply_text,
        parse_mode='HTML',
        reply_markup=kb.main_menu,
    )

@router.message(F.text == "Оставить отзыв")
async def start_review(msg: types.Message, state: FSMContext):
    await msg.answer("Оставьте, пожалуйста, отзыв:")
    await state.set_state(ReviewStates.waiting_for_review)


@router.message(F.text == "Изменить роль")
async def change_role(msg: types.Message, state: FSMContext):
    await msg.answer(
        "Выберите новую роль:",
        reply_markup=await kb.reply_roles(),
    )
    await state.set_state(ReviewStates.waiting_for_role)

@router.message(ReviewStates.waiting_for_contacts)
async def get_contacts(msg: types.Message, state: FSMContext) -> None:
    if msg.contact:
        await dbf.set_contact(
            chat_id=msg.from_user.id,
            phone=msg.contact.phone_number
        )
    
    reply_text = """✅ Спасибо! Ваше сообщение передано генеральному директору компании ДСК-1. Если вы оставили контакты — с вами свяжутся.""" 

    await msg.answer(
        text=reply_text,
        parse_mode='HTML',
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(ReviewStates.main_menu)
    await show_main_menu(msg, state)
