import os
import logging
import asyncio
import json
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.filters import CommandStart, Command
from aiogram.types import (
    BotCommand,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from middlewares.user_logger import UserLoggerMiddleware
from config import BOT_TOKEN
from scheduler.reminders import setup_reminders
from handlers import start, events, calendar, reminders, help, admin

# --- Настройка логов ---
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)
log_filename = os.path.join(LOG_DIR, f"bot_{datetime.now().strftime('%Y-%m-%d')}.log")

for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

file_handler = logging.FileHandler(log_filename, encoding="utf-8")
console_handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
logging.root.addHandler(file_handler)
logging.root.addHandler(console_handler)
logging.root.setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)
logger.info("🚀 Логирование инициализировано")


# --- Главное меню ---
async def set_main_menu(bot: Bot):
    commands = [
        BotCommand(command="start", description="📋 Главное меню"),
        BotCommand(command="mystarts", description="🚴 Мои старты"),
      #  BotCommand(command="races", description="🚴 Все гонки"),
        BotCommand(command="show_contacts", description="📞 Контакты"),
        BotCommand(command="help", description="❓ Помощь"),
        BotCommand(command="users", description="👥 Список пользователей"),
    ]
    await bot.set_my_commands(commands)


# --- Функция: показать гонку по ID ---
async def show_race_info(message: types.Message, race_id: str):
    try:
        with open("data/races.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        await message.answer("❌ Файл с гонками не найден.")
        return

    # убираем race_ из id если есть
    if race_id.startswith("race_"):
        race_id = race_id.replace("race_", "")

    race = None
    for category in data.get("categories", []):
        for r in category.get("races", []):
            if str(r["id"]) == str(race_id):
                race = r
                break
        if race:
            break

    if not race:
        await message.answer("❌ Гонка не найдена.")
        return

    # Клавиатура
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💾 Добавить в мои старты", callback_data=f"add_race_{race['id']}")],
        [InlineKeyboardButton(text="🌐 Перейти на сайт", url=race["url"])]
    ])

    text = (
        f"🚴‍♂️ <b>{race['name']}</b>\n"
        f"📅 {race['date']} {race['time']}\n"
        f"📍 {race['location']}\n"
        f"📏 {race['distance']}\n"
        f"🏢 Организатор: {race['org']}\n\n"
        f"{race['description']}"
    )

    await message.answer(text, parse_mode="HTML", reply_markup=keyboard)


# --- Deep-link /start ---
async def start_handler(message: types.Message, command: CommandStart):
    args = command.args
    if args:
        await show_race_info(message, args)
    else:
        await message.answer(
            "Привет! Это бот Велопульс 🚴‍♂️\n"
            "Отправь /races чтобы увидеть все доступные гонки."
        )


# --- Добавление гонки в “Мои старты” ---
async def add_race_to_mystarts(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    race_id = callback.data.replace("add_race_", "")

    os.makedirs("data/users", exist_ok=True)
    user_file = f"data/users/{user_id}.json"

    if os.path.exists(user_file):
        with open(user_file, "r", encoding="utf-8") as f:
            user_data = json.load(f)
    else:
        user_data = {"starts": []}

    if race_id not in user_data["starts"]:
        user_data["starts"].append(race_id)
        with open(user_file, "w", encoding="utf-8") as f:
            json.dump(user_data, f, ensure_ascii=False, indent=2)
        await callback.message.answer("✅ Гонка добавлена в твои старты!")
    else:
        await callback.message.answer("ℹ️ Эта гонка уже есть в твоём списке.")

    await callback.answer()


# --- Показ всех гонок ---
async def list_races(message: types.Message):
    try:
        with open("data/races.json", "r", encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        await message.answer("❌ Файл с гонками не найден.")
        return

    bot_username = "raceevent_bot"  # замени на реальное имя бота

    for category in data.get("categories", []):
        title = category.get("title", "Без категории")
        await message.answer(f"<b>{title}</b>", parse_mode="HTML")

        for race in category.get("races", []):
            race_id = f"race_{race['id']}"
            race_link = f"https://t.me/{bot_username}?start={race_id}"

            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📲 Открыть в боте", url=race_link)]
            ])

            text = (
                f"🚴‍♂️ <b>{race['name']}</b>\n"
                f"📅 {race['date']} {race['time']}\n"
                f"📍 {race['location']}\n"
                f"📏 {race['distance']}\n"
                f"🌐 <a href='{race['url']}'>Сайт</a>"
            )

            await message.answer(text, reply_markup=keyboard, parse_mode="HTML")


# --- Основная функция ---
async def main():
    logging.info("🚀 Запуск Race Event Bot...")
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()

    setup_reminders(bot)
    dp.message.middleware(UserLoggerMiddleware())

    # Роутеры
    dp.include_router(start.router)
    dp.include_router(events.router)
    dp.include_router(calendar.router)
    dp.include_router(reminders.router)
    dp.include_router(help.router)
    dp.include_router(admin.router)

    # Команды
    dp.message.register(start_handler, CommandStart(deep_link=True))
    dp.message.register(list_races, Command("races"))
    dp.callback_query.register(add_race_to_mystarts, lambda c: c.data.startswith("add_race_"))

    await set_main_menu(bot)
    logger.info("✅ Бот запущен и слушает обновления...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
