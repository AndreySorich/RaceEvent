import os
import uuid
import datetime
from aiogram import Router, types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from ics import Calendar, Event, DisplayAlarm
from handlers.events import load_races

router = Router()

ICS_DIR = "C:/inetpub/wwwroot/raceevent/ics"  # папка на сервере
BASE_URL = "https://bot.a-sorich.ru/raceevent/ics"  # URL к ics-файлам

@router.callback_query(F.data.startswith("add_to_calendar_"))
async def add_to_calendar(callback: types.CallbackQuery):
    race_id = callback.data.replace("add_to_calendar_", "")
    races_data = load_races()

    race = None
    for cat in races_data["categories"]:
        for r in cat["races"]:
            if str(r["id"]) == race_id:
                race = r
                break
        if race:
            break

    if not race:
        await callback.answer("⚠️ Гонка не найдена", show_alert=True)
        return

    # --- Создаём событие ---
    e = Event()
    e.name = f"Гонка: {race['name']}"
    e.location = race.get("location", "")
    e.description = (
        f"📍 {race.get('location', '')}\n"
        f"📏 {race.get('distance', '')}\n"
        f"🌐 {race.get('org', '')}\n"
        f"🔗 {race.get('link', '')}"
    )

    date_str = race.get("date", "01.01.2025")
    time_str = race.get("time", "09:00")

    start_dt = datetime.datetime.strptime(f"{date_str} {time_str}", "%d.%m.%Y %H:%M")
    e.begin = start_dt
    e.end = start_dt + datetime.timedelta(hours=3)

    e.uid = f"{uuid.uuid4()}@velopuls"
    e.created = datetime.datetime.utcnow()
    e.dtstamp = datetime.datetime.utcnow()

    # --- Добавляем напоминания ---
    e.alarms.append(DisplayAlarm(trigger=datetime.timedelta(days=-1), display_text="Гонка завтра!"))
    e.alarms.append(DisplayAlarm(trigger=datetime.timedelta(hours=-1), display_text="Гонка через час!"))

    # --- Сохраняем .ics файл ---
    os.makedirs(ICS_DIR, exist_ok=True)
    ics_filename = f"{race['id']}.ics"
    ics_path = os.path.join(ICS_DIR, ics_filename)
    with open(ics_path, "w", encoding="utf-8") as f:
        f.write(Calendar(events=[e]).serialize())

    # --- Формируем ссылку ---
    html_page = f"""
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Добавить гонку в календарь</title>
    </head>
    <body style="font-family: Arial; text-align: center; padding-top: 50px;">
        <h2>📅 {race['name']}</h2>
        <p>Нажми, чтобы добавить гонку в календарь:</p>
        <a href="{BASE_URL}/{ics_filename}" style="font-size:18px;">➡️ Добавить в календарь</a>
    </body>
    </html>
    """

    html_filename = f"{race['id']}.html"
    html_path = os.path.join(ICS_DIR, html_filename)
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_page)

    http_link = f"{BASE_URL}/{html_filename}"

    # --- Кнопка в Telegram ---
    kb = InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="📅 Добавить в календарь", url=http_link)]]
    )

    await callback.message.answer(
        f"📆 Гонка <b>{race['name']}</b> готова к добавлению в календарь.\n"
        "Нажми кнопку ниже 👇",
        reply_markup=kb
    )

    await callback.answer()
