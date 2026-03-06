from aiogram import Router, types
from aiogram.filters import Command

router = Router()

@router.message(Command("help"))
async def cmd_help(message: types.Message):
    text = (
        "ℹ️ <b>Race Event Bot — твой спортивный помощник</b> 🚴‍♂️\n\n"
        "Я помогу тебе:\n"
        "• 📅 Следить за стартами\n"
        "• 📆 Добавлять гонки в календарь\n"
        "• 🔔 Получать напоминания\n"
        "• 🌦 Смотреть погоду перед стартом\n\n"
        "📌 Основные команды:\n"
        "/start — Главное меню\n"
        "/mystarts — Твои старты\n"
        "/show_contacts — Контакты\n\n"
        "💡 <i>Совет:</i> добавь меня в избранное, чтобы быть готовым к каждому старту!"
    )
    await message.answer(text, parse_mode="HTML")
