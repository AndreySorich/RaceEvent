from aiogram import Router, types, F
import logging

router = Router()

@router.callback_query(F.data == "my_events")
async def show_my_events(callback: types.CallbackQuery):
    user = callback.from_user
    logging.info(f"{user.full_name} нажал кнопку '📅 Мои старты'")
    await callback.message.answer("🏁 Твои ближайшие старты:\n• Gran Fondo Moscow — 25 мая\n• LaStrada Tver — 8 июня")
    await callback.answer()

@router.callback_query(F.data == "reminder")
async def set_reminder(callback: types.CallbackQuery):
    user = callback.from_user
    logging.info(f"{user.full_name} установил напоминание о старте")
    await callback.message.answer("🔔 Напоминание установлено за 1 день до старта!")
    await callback.answer()

@router.callback_query(F.data == "add_calendar")
async def add_to_calendar(callback: types.CallbackQuery):
    user = callback.from_user
    logging.info(f"{user.full_name} добавил гонку в календарь")
    await callback.message.answer("📆 Гонка добавлена в твой календарь (.ics)")
    await callback.answer()

@router.callback_query(F.data == "help")
async def show_help(callback: types.CallbackQuery):
    user = callback.from_user
    logging.info(f"{user.full_name} открыл меню 'ℹ️ Возможности'")
    await callback.message.answer(
        "ℹ️ Race Event — твой помощник:\n"
        "• Следи за стартами\n"
        "• Добавляй гонки в календарь\n"
        "• Получай напоминания\n"
        "• Смотри погоду перед гонкой"
    )
    await callback.answer()
