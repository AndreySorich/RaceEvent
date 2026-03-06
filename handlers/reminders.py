from aiogram import Router, Bot
import asyncio
import json
from datetime import datetime, timedelta

router = Router()  # ✅ Добавили, чтобы dp.include_router(reminders.router) работал


RACES_FILE = "data/races.json"
USER_EVENTS_FILE = "data/user_events.json"


def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


async def check_reminders(bot: Bot):
    """Фоновая проверка гонок и отправка напоминаний"""
    print("🔔 Reminder task started...")

    while True:
        try:
            now = datetime.now()
            user_events = load_json(USER_EVENTS_FILE)
            races_data = load_json(RACES_FILE)
            all_races = [r for c in races_data.get("categories", []) for r in c.get("races", [])]

            for user_id, race_ids in user_events.items():
                for race_id in race_ids:
                    race = next((r for r in all_races if str(r.get("id")) == str(race_id)), None)
                    if not race:
                        continue

                    # Парсим дату гонки
                    try:
                        race_date = datetime.strptime(race["date"], "%Y-%m-%d")  # формат 2025-08-10
                    except ValueError:
                        try:
                            race_date = datetime.strptime(race["date"], "%d.%m.%Y")  # формат 10.08.2025
                        except ValueError:
                            continue

                    # Интервалы напоминаний
                    reminders = [
                        (7, "⏳ Осталась неделя до гонки!"),
                        (2, "⚡ Через 2 дня старт!"),
                        (0, "🚴 Старт через 2 часа!")
                    ]

                    for days_before, message in reminders:
                        reminder_time = race_date - timedelta(days=days_before)
                        # если осталось 2 часа — корректируем под часы
                        if days_before == 0:
                            reminder_time = race_date - timedelta(hours=2)

                        # Проверяем совпадение по дате/времени
                        if abs((now - reminder_time).total_seconds()) < 60:  # ±1 минута
                            text = (
                                f"{message}\n\n"
                                f"🏁 <b>{race['name']}</b>\n"
                                f"📅 {race['date']} ⏰ {race.get('time', '-')}\n"
                                f"📍 {race['location']}\n\n"
                                f"🔗 <a href='{race['link']}'>Подробнее</a>"
                            )
                            await bot.send_message(chat_id=int(user_id), text=text, parse_mode="HTML")
                            print(f"[REMINDER] Sent to {user_id}: {race['name']} ({message})")

            await asyncio.sleep(60)  # проверка каждую минуту

        except Exception as e:
            print(f"[ERROR in reminders] {e}")
            await asyncio.sleep(60)
