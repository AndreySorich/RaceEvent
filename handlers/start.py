from aiogram import Router, types
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from utils.storage import add_event_for_user
from utils.data_loader import load_races
from utils.storage import add_event_for_user, get_user_events
from utils.data_loader import load_races
from aiogram import Bot, Dispatcher, Router, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
import asyncio
import logging
router = Router()

from aiogram import types, Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext

router = Router()



from aiogram import F

logging.basicConfig(level=logging.INFO)

TOKEN = "8432313674:AAF60FZ7wzrjTK4j3necHE-i7RWFK1CrOeE"

bot = Bot(token=TOKEN)
dp = Dispatcher()





#---перезапуск если юзер удалил и снова вошел ----
@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.clear()  # сбрасывает старое состояние, если оно зависло
    await message.answer(
        "🏁 Выбери категорию ниже, чтобы начать:",
        reply_markup=main_menu()  # используем нашу функцию
   
    )


# --- Главное меню ---
def main_menu():
    kb = InlineKeyboardBuilder()
    kb.button(text="🚴 Гонки на шоссе", callback_data="race_road")
    kb.button(text="🏟️ Гонки на треке", callback_data="race_trek")
    kb.button(text="🏊‍♂️ Триатлон", callback_data="race_thriatlon")
    kb.button(text="🚴‍♂️ Клубные заезды", callback_data="race_club")
    kb.button(text="⭐ Мои старты", callback_data="my_events")
    kb.button(text="🧭 Контакты", callback_data="contact")
    kb.adjust(2)
    return kb.as_markup()


# --- Кнопка назад ---
def back_button():
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ Назад", callback_data="back_to_menu")
    return kb.as_markup()

# --- Меню  Шоссейные Гонки ---
from aiogram.utils.keyboard import InlineKeyboardBuilder

# Главное меню
@router.message(F.text == "📋 Главное меню")
async def show_main_menu(message: types.Message):
    await message.answer("🏁 Главное меню:", reply_markup=main_menu())



# --- Команда  для бововой менюхи /show_contacts ---
@router.message(Command("show_contacts"))
async def cmd_show_contacts(message: types.Message):
    text = (
        "ℹ️ <b>Контакты Race Event:</b>\n\n"
        "🌐 @a_sorich — ответит на вопросы \n"
        "📢 @race_repotr - Канал Race Report"
    )
    await message.answer(text, parse_mode="HTML")



# Контакты
@router.message(F.text == "📞 Контакты")
async def show_contacts(message: types.Message):
    await message.answer(
        "ℹ️ Контакты Race Event:\n"
        "🌐 @a_sorich — ответит на вопросы\n"
        "📢 @race_repotr - Канал Race Report"
    )

# 🔄 Обновить список стартов
@router.message(F.text == "🔄 Обновить старты")
async def refresh_races(message: types.Message):
    try:
        data = load_races()
        count = sum(len(cat["races"]) for cat in data["categories"])
        await message.answer(f"✅ Список стартов обновлён! Сейчас доступно {count} гонок.", reply_markup=main_menu())
    except Exception as e:
        await message.answer(f"⚠️ Ошибка при обновлении стартов:\n<code>{e}</code>", parse_mode="HTML")




# --- Команда /start ---
from aiogram.filters import CommandStart

user_starts = {}  # простое хранилище для теста (user_id: [race_ids])




# --- Обработчики кнопок ---
from utils.data_loader import load_races
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram import types, F

# --- Обработчики кнопок шоссейные гонки ---
import json
from aiogram import Router, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder



# Загрузка JSON
def load_races():
    with open("data/races.json", "r", encoding="utf-8") as f:
        return json.load(f)
        


# --- Клавиатура действий для гонки ---
def race_action_kb(race_id: int, source: str):
    kb = InlineKeyboardBuilder()

    if source == "my_events":
        kb.button(text="📅 В календарь", callback_data=f"add_to_calendar_{race_id}")
        kb.button(text="🗑 Удалить", callback_data=f"delete_event_{race_id}")
        kb.button(text="⬅️ Назад", callback_data="back_to_my_events")
    else:
        kb.button(text="📅 В календарь", callback_data=f"add_to_calendar_{race_id}")
        kb.button(text="➕ В мои старты", callback_data=f"add_event_{race_id}")
        kb.button(text="⬅️ Назад", callback_data="back_to_menu")

    kb.adjust(2)
    return kb.as_markup()

#---Проверяет, что дата гонки в будущем (сегодня включительно) -----
import datetime

def is_future_race(date_str: str) -> bool:
    """Проверяет, что дата гонки в будущем (сегодня включительно)."""
    race_date = datetime.datetime.strptime(date_str, "%d.%m.%Y").date()
    today = datetime.date.today()
    return race_date >= today

        
        
# --- обработчик гонок на шоссе -----
@router.callback_query(F.data == "race_road")
async def show_road_races(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(last_menu="race_road")    
    data = load_races()
    road_races = next(cat for cat in data["categories"] if cat["type"] == "road")["races"]

    text = "<b>🚴 Доступные шоссейные гонки за 60 дней:</b>\n\n"
    await callback.message.answer(text, parse_mode="HTML")

    for race in road_races:
        if not is_future_race(race["date"]):
            continue

        text = (
            f"🏁 <b>{race['name']}</b>\n"
            f"📅 {race['date']} | {race['time']}\n"
            f"📍 {race['location']}\n"
            f"📏 {race['distance']}\n"
        )

        kb = InlineKeyboardBuilder()
        kb.button(text="➕ Добавить в мои старты", callback_data=f"add_event_{race['id']}")
        kb.button(text="🔍 Открыть гонку", callback_data=f"view_race_{race['id']}:road")
        kb.adjust(2)

        await callback.message.answer(
            text,
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=kb.as_markup()
        )

    # --- В самом низу: кнопка "⬅️ Назад" ---
    kb_back = InlineKeyboardBuilder()
    kb_back.button(text="⬅️ Назад", callback_data="back_to_menu")

    await callback.message.answer(
        "👇 Навигация:",
        reply_markup=kb_back.as_markup()
    )

    await callback.answer()
    # 👇 Кнопки "⭐ Мои старты" и "⬅️ Меню" в конце списка
  #  kb_bottom = InlineKeyboardBuilder()
  #  kb_bottom.button(text="⭐ Мои старты", callback_data="my_events")
  #  kb_bottom.button(text="🏁 Меню", callback_data="back_to_menu")
  #  kb_bottom.adjust(2)

  #  await callback.message.answer(
  #      "👇 Навигация:", reply_markup=kb_bottom.as_markup()
  # )

    await callback.answer()

#--- Обработчик гонок на треке---
@router.callback_query(F.data == "race_trek")
async def show_trek_races(callback: types.CallbackQuery):
    data = load_races()
    
    # ищем категорию с типом trek
    trek_races = next(
        cat["races"] for cat in data["categories"] if cat["type"] == "trek"
    )

    text = "<b>🏟️ Доступные гонки на треке за 60 дней:</b>\n\n"
    await callback.message.answer(text, parse_mode="HTML")

    for race in trek_races:
        if not is_future_race(race["date"]):
            continue

        text = (
            f"🏁 <b>{race['name']}</b>\n"
            f"📅 {race['date']} | {race['time']}\n"
            f"📍 {race['location']}\n"
            f"📏 {race.get('distance', '—')}\n"
        )

        kb = InlineKeyboardBuilder()
        kb.button(
            text="➕ Добавить в мои старты",
            callback_data=f"add_event_{race['id']}"
        )
        kb.button(
            text="🔍 Открыть гонку",
            callback_data=f"view_race_{race['id']}:trek"
        )
        kb.adjust(2)

        await callback.message.answer(
            text,
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=kb.as_markup()
        )

    # --- В самом низу: кнопка "⬅️ Назад" ---
    kb_back = InlineKeyboardBuilder()
    kb_back.button(text="⬅️ Назад", callback_data="back_to_menu")

    await callback.message.answer(
        "👇 Навигация:",
        reply_markup=kb_back.as_markup()
    )

    await callback.answer()

#    # 👇 Кнопки "⭐ Мои старты" и "⬅️ Меню" в конце списка
#    kb_bottom = InlineKeyboardBuilder()
#    kb_bottom.button(text="⭐ Мои старты", callback_data="my_events")
#    kb_bottom.button(text="🏁 Меню", callback_data="back_to_menu")
#    kb_bottom.adjust(2)
#
#    await callback.message.answer(
#        "👇 Навигация:", reply_markup=kb_bottom.as_markup()
#    )
#
#    await callback.answer()

#--- Обработчик клубных заездов ------
@router.callback_query(F.data == "race_club")
async def show_club_rides(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(last_menu="race_club")

    data = load_races()
    club_rides = next(
        cat["races"] for cat in data["categories"] if cat["type"] == "club"
    )

    text = "<b>🚴‍♂️ Клубные заезды :</b>\n\n"
    await callback.message.answer(text, parse_mode="HTML")

    for race in club_rides:
        if not is_future_race(race["date"]):
            continue

        text = (
            f"🏁 <b>{race['name']}</b>\n"
            f"📅 {race['date']} | {race['time']}\n"
            f"📍 {race['location']}\n"
            f"📏 {race.get('distance', '—')}\n"
        )

        kb = InlineKeyboardBuilder()
        kb.button(text="➕ Добавить в мои старты", callback_data=f"add_event_{race['id']}")
        kb.button(text="🔍 Открыть заезд", callback_data=f"view_race_{race['id']}:club")
        kb.adjust(2)

        await callback.message.answer(
            text,
            parse_mode="HTML",
            disable_web_page_preview=True,
            reply_markup=kb.as_markup()
        )

    kb_back = InlineKeyboardBuilder()
    kb_back.button(text="⬅️ Назад", callback_data="back_to_menu")

    await callback.message.answer("👇 Навигация:", reply_markup=kb_back.as_markup())
    await callback.answer()




#--- Обработчики добавить гонку с ID ---

import json
from pathlib import Path

USER_EVENTS_FILE = Path("data/user_events.json")


def load_user_events():
    if USER_EVENTS_FILE.exists():
        with open(USER_EVENTS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_user_events(data):
    with open(USER_EVENTS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


@router.callback_query(F.data.startswith("add_event_"))
async def add_event(callback: types.CallbackQuery):
    user_id = str(callback.from_user.id)
    race_id = callback.data.replace("add_event_", "")

    data = load_user_events()
    user_events = data.get(user_id, [])


    if race_id not in user_events:
        user_events.append(race_id)
        data[user_id] = user_events
        save_user_events(data)
        await callback.answer("✅ Добавлено в твои старты!", show_alert=False)
    else:
        await callback.answer("⚠️ Уже добавлено ранее", show_alert=False)


    
    


# --- Обработчик "Мои старты" ---
import datetime
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- Обработчик "Мои старты" ---
@router.callback_query(F.data == "my_events")
async def show_my_events(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(last_menu="my_events")
    user_id = str(callback.from_user.id)
    data = load_user_events()
    user_events = data.get(user_id, [])

    if not user_events:
        await callback.message.edit_text(
            "⭐ У тебя пока нет добавленных стартов.",
            reply_markup=back_button()
        )
        await callback.answer()
        return

    races_data = load_races()
    all_races = []
    for cat in races_data["categories"]:
        all_races.extend(cat["races"])

    now = datetime.datetime.now()
    future_races = []

    for race_id in user_events:
        race = next((r for r in all_races if str(r["id"]) == str(race_id)), None)
        if not race:
            continue

        # Парсим дату и время гонки
        race_datetime = datetime.datetime.strptime(f"{race['date']} {race.get('time','00:00')}", "%d.%m.%Y %H:%M")

        if race_datetime >= now:
            future_races.append(race)

    if not future_races:
        await callback.message.edit_text(
            "⭐ У тебя нет будущих стартов.",
            reply_markup=back_button()
        )
        await callback.answer()
        return

    text = "<b>⭐ Твои будущие старты:</b>\n\n"
    await callback.message.edit_text(text, parse_mode="HTML")

    for race in future_races:
        text = (
            f"🏁 <b>{race['name']}</b>\n"
            f"📅 {race['date']} {race.get('time','')}\n"
            f"📍 {race['location']}\n"
            f"📏 {race['distance']}\n"
        )

        kb = InlineKeyboardBuilder()
        kb.button(text="🗑 Удалить", callback_data=f"delete_event_{race['id']}")
        kb.button(text="🔍 Открыть гонку", callback_data=f"view_race_{race['id']}:my_events")
        kb.adjust(2)

        await callback.message.answer(text, parse_mode="HTML", reply_markup=kb.as_markup())

    kb_nav = InlineKeyboardBuilder()
    kb_nav.button(text="Прошедшие ➡️", callback_data="my_events_past")
    kb_nav.button(text="⬅️ Меню", callback_data="back_to_menu")
    kb_nav.adjust(2)

    await callback.message.answer(
        "👇 Навигация:",
        reply_markup=kb_nav.as_markup()
    )
    await callback.answer()


# --- Обработчик кнопки "Прошедшие" ---
@router.callback_query(F.data == "my_events_past")
async def show_my_events_past(callback: types.CallbackQuery):
    user_id = str(callback.from_user.id)
    data = load_user_events()
    user_events = data.get(user_id, [])

    races_data = load_races()
    all_races = []
    for cat in races_data["categories"]:
        all_races.extend(cat["races"])

    now = datetime.datetime.now()
    past_races = []

    for race_id in user_events:
        race = next((r for r in all_races if str(r["id"]) == str(race_id)), None)
        if not race:
            continue

        race_datetime = datetime.datetime.strptime(f"{race['date']} {race.get('time','00:00')}", "%d.%m.%Y %H:%M")

        if race_datetime < now:
            past_races.append(race)

    if not past_races:
        await callback.message.edit_text(
            "⭐ У тебя нет прошедших стартов.",
            reply_markup=back_button()
        )
        await callback.answer()
        return

    text = "<b>⭐ Твои прошедшие старты:</b>\n\n"
    await callback.message.edit_text(text, parse_mode="HTML")

    for race in past_races:
        text = (
            f"🏁 <b>{race['name']}</b>\n"
            f"📅 {race['date']} {race.get('time','')}\n"
            f"📍 {race['location']}\n"
            f"📏 {race['distance']}\n"
        )

        kb = InlineKeyboardBuilder()
        kb.button(text="🔍 Открыть гонку", callback_data=f"view_race_{race['id']}:my_events")
        kb.adjust(1)

        await callback.message.answer(text, parse_mode="HTML", reply_markup=kb.as_markup())

    kb_nav = InlineKeyboardBuilder()
    kb_nav.button(text="⬅️ Будущие старты", callback_data="my_events")
    kb_nav.button(text="⬅️ Меню", callback_data="back_to_menu")
    kb_nav.adjust(2)

    await callback.message.answer(
        "👇 Навигация:",
        reply_markup=kb_nav.as_markup()
    )
    await callback.answer()



import datetime
from aiogram.utils.keyboard import InlineKeyboardBuilder



# --- Команда /mystarts боковое меню  ---
@router.message(Command("mystarts"))
async def cmd_my_starts(message: types.Message, state: FSMContext):
    """Открывает раздел 'Мои старты' через команду /mystarts"""
    user_id = str(message.from_user.id)
    data = load_user_events()
    user_events = data.get(user_id, [])

    if not user_events:
        await message.answer(
            "⭐ У тебя пока нет добавленных стартов.",
            reply_markup=back_button()
        )
        return

    races_data = load_races()
    all_races = []
    for cat in races_data["categories"]:
        all_races.extend(cat["races"])

    now = datetime.datetime.now()
    future_races = []

    for race_id in user_events:
        race = next((r for r in all_races if str(r["id"]) == str(race_id)), None)
        if not race:
            continue

        # Парсим дату и время гонки
        race_datetime = datetime.datetime.strptime(f"{race['date']} {race.get('time','00:00')}", "%d.%m.%Y %H:%M")

        if race_datetime >= now:
            future_races.append(race)

    if not future_races:
        await message.answer(
            "⭐ У тебя нет будущих стартов.",
            reply_markup=back_button()
        )
        return

    text = "<b>⭐ Твои будущие старты:</b>\n\n"
    await message.answer(text, parse_mode="HTML")

    for race in future_races:
        text = (
            f"🏁 <b>{race['name']}</b>\n"
            f"📅 {race['date']} {race.get('time','')}\n"
            f"📍 {race['location']}\n"
            f"📏 {race['distance']}\n"
        )

        kb = InlineKeyboardBuilder()
        kb.button(text="🗑 Удалить", callback_data=f"delete_event_{race['id']}")
        kb.button(text="🔍 Открыть гонку", callback_data=f"view_race_{race['id']}:my_events")
        kb.adjust(2)

        await message.answer(text, parse_mode="HTML", reply_markup=kb.as_markup())

    # --- Навигация ---
    kb_bottom = InlineKeyboardBuilder()
    kb_bottom.button(text="⬅️ Назад в меню", callback_data="back_to_menu")
    kb_bottom.adjust(1)

    await message.answer("👇 Навигация:", reply_markup=kb_bottom.as_markup())


            # 👇 Кнопки "⭐ Мои старты" и "⬅️ Меню" в конце списка
 #    kb_bottom = InlineKeyboardBuilder()
 #   kb_bottom.button(text="⭐ Мои старты", callback_data="my_events")
 #   kb_bottom.button(text="🏁 Меню", callback_data="back_to_menu")
  #   kb_bottom.adjust(2)

  #   await callback.message.answer(
  #       "👇 Навигация:", reply_markup=kb_bottom.as_markup()
  #   )

   #  await callback.answer()
 #
    # кнопка назад внизу
#    kb_back = InlineKeyboardBuilder()
#    kb_back.button(text="⬅️ Назад", callback_data="back_to_menu")
#    await callback.message.answer("\u200B", reply_markup=kb_back.as_markup())
#
#    await callback.answer()




    #---Обработчик удаления гонки ----
@router.callback_query(F.data.startswith("delete_event_"))
async def delete_event(callback: types.CallbackQuery):
    """Удаляет гонку из списка пользователя"""
    user_id = str(callback.from_user.id)
    race_id = callback.data.replace("delete_event_", "")

    data = load_user_events()
    user_events = data.get(user_id, [])

    if race_id in user_events:
        user_events.remove(race_id)
        data[user_id] = user_events
        save_user_events(data)
        await callback.answer("🗑 Гонка удалена.")
        await callback.message.delete()
    else:
        await callback.answer("⚠️ Гонка не найдена в твоих стартах.", show_alert=True)

    #---Обработчик добавить в календарь ----
from aiogram import types, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from ics import Calendar, Event, DisplayAlarm
import datetime, os, uuid, pytz

ICS_DIR = r"C:\inetpub\wwwroot\bot\ics"
BASE_URL = "https://raceevent.ru/bot/ics"

@router.callback_query(F.data.startswith("add_to_calendar_"))
async def add_to_calendar(callback: types.CallbackQuery):
    race_id = callback.data.replace("add_to_calendar_", "")
    races_data = load_races()

    # Находим гонку
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

    os.makedirs(ICS_DIR, exist_ok=True)

    # --- Создаём событие ---
    e = Event()
    e.name = race["name"]
    e.location = race.get("location", "")
    e.description = f"📍 {race.get('location', '')}\n📏 {race.get('distance', '')}\n🌐 {race.get('org', '')}\n🔗 {race.get('link', '')}"

    # --- Дата и время ---
    date_str = race["date"]
    time_str = race.get("time", "09:00")

    # Указываем московский часовой пояс
    moscow_tz = pytz.timezone("Europe/Moscow")

    start_dt = datetime.datetime.strptime(f"{date_str} {time_str}", "%d.%m.%Y %H:%M")
    start_dt = moscow_tz.localize(start_dt)

    e.begin = start_dt
    e.end = start_dt + datetime.timedelta(hours=3)
    e.uid = f"{uuid.uuid4()}@race_event_news"
    e.created = datetime.datetime.now(moscow_tz)
    e.dtstamp = datetime.datetime.now(moscow_tz)

    # --- Напоминания ---
    e.alarms.append(DisplayAlarm(trigger=datetime.timedelta(days=-1), display_text="Напоминание: гонка завтра!"))
    e.alarms.append(DisplayAlarm(trigger=datetime.timedelta(hours=-1), display_text="Напоминание: гонка через 1 час!"))

    c = Calendar()
    c.events.add(e)

    # --- Сохраняем .ics ---
    ics_path = os.path.join(ICS_DIR, f"{race_id}.ics")
    with open(ics_path, "w", encoding="utf-8") as f:
        f.write(c.serialize())

    # --- Создаём HTML-страницу ---
    event_name = race["name"].replace('"', '&quot;')
    google_link = (
    "https://calendar.google.com/calendar/render"
    f"?action=TEMPLATE&text={event_name}"
    f"&dates={start_dt.strftime('%Y%m%dT%H%M%S')}/{(start_dt+datetime.timedelta(hours=3)).strftime('%Y%m%dT%H%M%S')}"
    f"&details={race.get('link','')}&location={race.get('location','')}"
    )

# --- ВАЖНО: определяем переменные ДО html_content ---
    description = race.get("description", "Описание скоро появится.")
    location = race.get("location", "-")
    distance = race.get("distance", "-")
    org = race.get("org", "-")
    link = race.get("link", "-")
    time_str = race.get("time", "-")
    date_str = race.get("date", "-")

    html_content = f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<title>{event_name} — добавить в календарь</title>
<style>
body {{
    font-family: Arial, sans-serif;
    text-align: center;
    padding: 40px;
    background: #f8f9fa;
    color: #333;
}}
h1 {{
    color: #222;
}}
a.button {{
    display: block;
    margin: 12px auto;
    padding: 12px 20px;
    border-radius: 8px;
    text-decoration: none;
    width: 250px;
    font-weight: bold;
    transition: 0.2s;
}}
a.apple {{
    background: #007AFF;
    color: white;
}}
a.google {{
    background: #DB4437;
    color: white;
}}
a.download {{
    background: #6c757d;
    color: white;
}}
a:hover {{
    opacity: 0.85;
}}
.details {{
    max-width: 600px;
    margin: 30px auto;
    text-align: left;
    background: #fff;
    border-radius: 10px;
    padding: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}}
.details p {{
    line-height: 1.6;
    margin: 6px 0;
}}
</style>
</head>
<body>
    <h1>📅 {event_name}</h1>
    <h2>ℹ️ Для телефонов Apple открой ссылку в Safari️ ℹ️</h2>
    <div class="details">
        <p><b>📅 Дата:</b> {date_str}</p>
        <p><b>⏰ Время:</b> {time_str}</p>
        <p><b>📍 Место:</b> {location}</p>
        <p><b>📏 Дистанция:</b> {distance}</p>
        <p><b>🌐 Организатор:</b> {org}</p>
        <p><b>📘 Описание:</b> {description}</p>
        <p><b>🔗 Сайт:</b> <a href="{link}" target="_blank">{link}</a></p>
    </div>
    <p>Выберите, куда добавить гонку:</p>
    <a class="button apple" href="{BASE_URL}/{race_id}.ics">Добавить в Apple Календарь</a>
    <a class="button google" href="{google_link}" target="_blank">Добавить в Google Календарь</a>
    <a class="button download" href="{BASE_URL}/{race_id}.ics" download>Скачать .ics файл</a>
</body>
</html>"""

    html_path = os.path.join(ICS_DIR, f"{race_id}.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write(html_content)

    # --- Отправляем ссылку пользователю ---
    page_url = f"{BASE_URL}/{race_id}.html"

    await callback.message.answer(
        f"📆 Гонка <b>{race['name']}</b> готова к добавлению в календарь!\n\n"
        f"ℹ️ <a><b>Для Apple открой ссылку в Safari</b>ℹ️</a>\n"
        f"🔗 {page_url}",
        parse_mode="HTML"
    )

    await callback.answer("✅ Ссылка на страницу календаря создана")
    # --- Кнопки "⭐ Мои старты" и "🏁 Меню" ---
    kb_bottom = InlineKeyboardBuilder()
    kb_bottom.button(text="⭐ Мои старты", callback_data="my_events")
    kb_bottom.button(text="🏁 Меню", callback_data="back_to_menu")
    kb_bottom.adjust(2)

    await callback.message.answer(
    "👇 Навигация:",
    reply_markup=kb_bottom.as_markup()
    )

# --- Кнопка "⬅️ Назад" ---
    kb_back = InlineKeyboardBuilder()
    kb_back.button(text="⬅️ Назад", callback_data="back_to_menu")

    await callback.message.answer("\u200B", reply_markup=kb_back.as_markup())
     


    #---Обработчик открыть карточку  гонки ----
@router.callback_query(F.data.startswith("view_race_"))
async def view_race(callback: types.CallbackQuery, state: FSMContext):
    """Показывает полное описание выбранной гонки"""
    user_id = str(callback.from_user.id)
    race_id = str(callback.data).replace("view_race_", "").split(":")[0].strip()

    # 🔍 DEBUG-лог
    print(f"[DEBUG] view_race: got race_id={race_id}")

    data = load_races()
    all_races = [r for cat in data["categories"] for r in cat["races"]]

    # 🔍 DEBUG-лог
    print(f"[DEBUG] all ids={[str(r.get('id')).strip() for r in all_races]}")
    print(f"[DEBUG] loaded {len(all_races)} races from file.")

    race = next((r for r in all_races if str(r.get("id")).strip() == race_id), None)
    if not race:
        await callback.answer("⚠️ Гонка не найдена.", show_alert=True)
        return

    # Узнаём, из какого меню пользователь пришёл
    last_context = await state.get_data()
    source = last_context.get("last_menu", "default")

    text = (
        f"🏁 <b>{race['name']}</b>\n\n"
        f"📅<b> Дата:</b> {race['date']}\n"
        f"⏰ <b>Время:</b> {race.get('time', '-')}\n"
        f"📍 <b>Место:</b> {race['location']}\n"
        f"📏 <b>Дистанция:</b> {race['distance']}\n"
        f"🌐 <b>Организатор:</b> {race.get('org', '-')}\n"
        f"📘 <b>Описание:</b> {race.get('description', '-')}\n"
        f"🔗 <a href='{race['link']}'>Подробнее</a>"
    )

    kb = InlineKeyboardBuilder()

    if source == "my_events":
        # Если открыт из "Мои старты"
        kb.button(text="📅 Добавить в календарь", callback_data=f"add_to_calendar_{race['id']}")
        kb.button(text="🗑 Удалить", callback_data=f"delete_event_{race['id']}")
        #kb.button(text="📤 Поделиться", callback_data=f"share_race_{race['id']}")#
        kb.button(text="⭐ Мои старты", callback_data="my_events")
    else:
        # Если открыт из списка гонок (например, "Гонки на шоссе")
        kb.button(text="📅 Добавить в календарь", callback_data=f"add_to_calendar_{race['id']}")
        kb.button(text="➕ В мои старты", callback_data=f"add_event_{race['id']}")
       # kb.button(text="📤 Поделиться", callback_data=f"share_race_{race['id']}")#
       # kb.button(text="⬅️ Назад", callback_data="back_to_races") #

    kb.button(text="🏁 Меню", callback_data="back_to_menu")
    kb.adjust(2)

    await callback.message.edit_text(
        text,
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=kb.as_markup()
    )
    await callback.answer()

@router.callback_query(F.data == "back_to_races")
async def back_to_races(callback: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    source = data.get("last_menu")

    if source == "race_road":
        await show_road_races(callback, state)
    elif source == "race_club":
        await show_club_rides(callback, state)
    elif source == "race_trek":
        await show_trek_races(callback)
    else:
        await callback.message.answer("🏁 Главное меню:", reply_markup=main_menu())
        await callback.answer()


#---Возврат в список стартов без пересоздания сообщений ----
#---!@router.callback_query(F.data == "back_to_my_events")
#---!async def back_to_my_events(callback: types.CallbackQuery):
#---!    """Возврат из карточки гонки обратно в список стартов"""
#---!    await show_my_events(callback)


#---Позволяет пользователю поделиться гонкой ----
@router.callback_query(F.data.startswith("share_race_"))
async def share_race(callback: types.CallbackQuery):
    """Позволяет пользователю поделиться гонкой"""
    race_id = callback.data.replace("share_race_", "").strip()
    data = load_races()
    all_races = [r for cat in data["categories"] for r in cat["races"]]
    race = next((r for r in all_races if str(r["id"]) == race_id), None)

    if not race:
        await callback.answer("⚠️ Гонка не найдена.", show_alert=True)
        return

    # 1️⃣ Текст для пересылки
    share_text = (
        f"🏁 {race['name']}\n"
        f"📅 {race['date']} ⏰ {race.get('time', '-')}\n"
        f"📍 {race['location']}\n"
        f"📏 {race['distance']}\n"
        f"🌐 Организатор: {race.get('org', '-')}\n\n"
        f"🔗 {race.get('link')}\n\n"
        f"🚴 Хочу участвовать в этой гонке!"
    )

    # 2️⃣ Ссылка для открытия карточки гонки в боте
    bot_username = (await callback.bot.get_me()).username
    deep_link = f"https://t.me/{bot_username}?start=race_{race_id}"

    await callback.message.answer(
        f"📤 Можешь поделиться гонкой с друзьями!\n\n"
        f"<b>Текст для пересылки:</b>\n{share_text}\n\n"
        f"<b>Ссылка для открытия в боте:</b>\n{deep_link}",
        disable_web_page_preview=True
    )
    await callback.answer()



 

@router.callback_query(F.data == "race_trek")
async def show_race_trek(callback: types.CallbackQuery):
    await callback.message.answer(
    "Ниже — основные организаторы, проводящие гонки на треке.\n"
    "Нажми на любого, чтобы посмотреть ближайшие гонки 👇", 
    reply_markup=trek_menu())
    await callback.answer()

@router.callback_query(F.data == "race_thriatlon")
async def show_triathlon(callback: types.CallbackQuery):
    await callback.message.answer("🏊‍️ Триатлон скоро появится)", reply_markup=back_button())
    await callback.answer()

@router.callback_query(F.data == "race_90day")
async def show_upcoming(callback: types.CallbackQuery):
    await callback.message.answer("📅 Ближайшие старты скоро появится)", reply_markup=back_button())
    await callback.answer()
    


@router.callback_query(F.data == "contact")
async def show_contacts(callback: types.CallbackQuery):
    await callback.message.answer(
        "ℹ️ Контакты Race Event:\n"
        "🌐 @a_sorich — ответит на вопросы\n"
        "📢 @race_repotr - Канал Race Report",
        reply_markup=back_button()
    )
    await callback.answer()


# --- Обработчик кнопки Назад ---
@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery):
    await callback.message.answer("🏁 Главное меню:", reply_markup=main_menu())
    await callback.answer()

# --- Обработчик кнопки Гонки на шоссе ---
@router.callback_query(F.data == "road_buttom")
async def road_buttom(callback: types.CallbackQuery):
    await callback.message.answer("🏁 Race Road:", reply_markup=road_menu())
    await callback.answer()
    
# --- Обработчик кнопки Гонки на треке ---
@router.callback_query(F.data == "trek_buttom")
async def trek_buttom(callback: types.CallbackQuery):
    await callback.message.answer("🏁 Race Road:", reply_markup=trek_menu())
    await callback.answer()

async def main():
    dp.include_router(router)
    print("🤖 Race Event Bot запущен. Ожидаю команды...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
