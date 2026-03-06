import json
import logging
from aiogram import Router, types
from aiogram.filters import Command

router = Router()

# 👉 Укажи свой Telegram ID
ADMIN_ID = 259810935  # замени на свой, если другой
USERS_FILE = "data/users.json"


@router.message(Command("users"))
async def show_users(message: types.Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("🚫 У вас нет доступа к этой команде.")
        return

    try:
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            users = json.load(f)
    except Exception as e:
        logging.error(f"Ошибка при чтении users.json: {e}")
        await message.answer("⚠️ Не удалось прочитать список пользователей.")
        return

    if not users:
        await message.answer("📭 Пока нет зарегистрированных пользователей.")
        return

    # Формируем HTML-текст
    text = f"<b>📊 Всего пользователей: {len(users)}</b>\n\n"
    for uid, info in users.items():
        uname = info.get("username", "unknown")
        reg_date = info.get("registered_at", "—")
        if uname != "unknown":
            text += f"🆔 <code>{uid}</code> — @{uname} (📅 {reg_date})\n"
        else:
            text += f"🆔 <code>{uid}</code> — без username (📅 {reg_date})\n"

    # Проверяем длину сообщения
    if len(text) > 4000:
        await message.answer(f"📊 Всего пользователей: {len(users)}")
        await message.answer_document(
            document=("users.json", json.dumps(users, ensure_ascii=False, indent=2).encode("utf-8")),
            caption="📎 Полный список пользователей",
        )
    else:
        await message.answer(text, parse_mode="HTML")
