import json
import logging
from aiogram import Router, types, F
from aiogram.utils.keyboard import InlineKeyboardBuilder

router = Router()

# === Загрузка данных о гонках ===
def load_races():
    try:
        with open("data/races.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logging.error(f"Ошибка загрузки races.json: {e}")
        return {"categories": []}

# === Главное меню гонок ===
@router.callback_query(F.data.in_({"race_road", "race_trek", "race_thriatlon", "race_90day"}))
async def show_category(callback: types.CallbackQuery):
    races_data = load_races()
    if not races_data["categories"]:
        await callback.message.answer("⚠️ Нет доступных гонок.")
        return

    cat_map = {
        "race_road": "Шоссе",
        "race_trek": "Трек",
        "race_thriatlon": "Триатлон",
        "race_90day": "Ближайшие старты"
    }
    category_name = cat_map.get(callback.data, "Неизвестная категория")

    # Ищем категорию
    category = next((c for c in races_data["categories"] if c["name"] == category_name), None)
    if not category:
        await callback.message.answer("⚠️ Категория не найдена.")
        return

    # Строим список гонок
    kb = InlineKeyboardBuilder()
    for race in category["races"]:
        kb.button(
            text=f"{race['name']} ({race['date']})",
            callback_data=f"view_race_{race['id']}"
        )
    kb.adjust(1)

    await callback.message.answer(
        f"🏁 <b>{category_name}</b>\nВыбери гонку из списка:",
        reply_markup=kb.as_markup()
    )
    await callback.answer()

# === Просмотр гонки ===
@router.callback_query(F.data.startswith("view_race_"))
async def view_race(callback: types.CallbackQuery):
    race_id = callback.data.replace("view_race_", "")
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
        await callback.message.answer("⚠️ Гонка не найдена.")
        return

    name = race.get("name", "Без названия")
    date = race.get("date", "—")
    time = race.get("time", "09:00")
    location = race.get("location", "Не указано")
    distance = race.get("distance", "—")
    org = race.get("org", "Не указан")
    link = race.get("link", "")

    text = (
        f"<b>{name}</b>\n\n"
        f"📅 Дата: {date}\n"
        f"⏰ Время: {time}\n"
        f"📍 Место: {location}\n"
        f"📏 Дистанция: {distance}\n"
        f"🌐 Организатор: {org}\n"
    )
    if link:
        text += f"🔗 <a href='{link}'>Подробнее</a>\n"

    kb = InlineKeyboardBuilder()
    kb.button(text="📅 Добавить в календарь", callback_data=f"add_to_calendar_{race_id}")
    kb.button(text="⬅️ Назад", callback_data="race_road")
    kb.adjust(1)

    await callback.message.answer(text, reply_markup=kb.as_markup())
    await callback.answer()
