import logging
from aiogram import Router, types, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from utils.keyboards import reply_main_keyboard, inline_main_menu

router = Router()

@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()
    first_name = message.from_user.first_name or "друг"

    text = (
        f"👋 Привет, {first_name}!\n\n"
        f"Я бот клуба <b>Велопульс</b> 🚴‍♂️\n"
        f"Помогаю следить за стартами и добавлять их в календарь.\n\n"
        f"Выбирай действие ниже:"
    )

    await message.answer(text, reply_markup=reply_main_keyboard())
    await message.answer("🏁 Главное меню:", reply_markup=inline_main_menu())

@router.message(F.text == "📞 Контакты")
async def show_contacts(message: types.Message):
    await message.answer(
        "ℹ️ Контакты клуба Велопульс:\n"
        "@a_sorich — ответит на вопросы\n"
        "📧 raceevent.pro@gmail.com\n"
        "📢 Канал: https://t.me/race_event_news"
    )

@router.message(F.text == "🏁 Главное меню")
async def show_main_menu(message: types.Message):
    await message.answer("🏁 Главное меню:", reply_markup=inline_main_menu())
