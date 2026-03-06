# reminders.py
import logging
import json
import aiohttp
import asyncio
import aiocron
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Optional, Dict, Any
from aiogram import Bot

# ----------------------------
# Конфигурация
# ----------------------------
RACES_FILE = "data/races.json"
USER_EVENTS_FILE = "data/user_events.json"
SENT_CACHE_FILE = "data/sent_reminders.json"
WEATHER_CACHE_FILE = "data/weather_cache.json"

WEATHER_API_KEY = "5b7da059dfb35593e9ef1a0cc4252a05"
LOCAL_TZ = ZoneInfo("Europe/Moscow")
CRON_EXPR = "*/5 * * * *"
WEATHER_TTL_SUCCESS = 6 * 3600
WEATHER_TTL_FAILURE = 15 * 60

# ----------------------------
# Утилиты
# ----------------------------
def now_tz() -> datetime:
    return datetime.now(LOCAL_TZ).replace(microsecond=0)

def parse_event_datetime(date_str: str, time_str: str) -> Optional[datetime]:
    for fmt in ("%d.%m.%Y %H:%M", "%Y-%m-%d %H:%M"):
        try:
            dt = datetime.strptime(f"{date_str} {time_str}", fmt)
            return dt.replace(tzinfo=LOCAL_TZ)
        except Exception:
            continue
    return None

# ----------------------------
# DataStorage
# ----------------------------
class DataStorage:
    @staticmethod
    def load_json(path: str) -> Any:
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return None

    @staticmethod
    def save_json(path: str, data: Any) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

# ----------------------------
# WeatherService
# ----------------------------
class WeatherService:
    def __init__(self, api_key: str, cache_path: str = WEATHER_CACHE_FILE):
        self.api_key = api_key
        self.cache_path = cache_path
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._load_cache()

    def _load_cache(self):
        data = DataStorage.load_json(self.cache_path)
        if isinstance(data, dict):
            self._cache = data

    def _save_cache(self):
        DataStorage.save_json(self.cache_path, self._cache)

    def _cache_key(self, location: str, date: datetime) -> str:
        return f"{location.strip().lower()}_{date.strftime('%Y-%m-%d')}"

    def _is_cache_valid(self, entry: Dict[str, Any]) -> bool:
        try:
            ts = datetime.fromisoformat(entry["timestamp"])
            ttl = entry.get("ttl", WEATHER_TTL_SUCCESS)
            return (now_tz() - ts).total_seconds() < ttl
        except Exception:
            return False

    async def get_weather(self, location: str, event_dt: datetime, race_type: str = None) -> str:
        if race_type == "trek":
            return "🌤️ <b>Погода:</b> На велотреке обычно комфортно.\n🌡️ +22°C, 💨 мало ветра"
        if not self.api_key:
            return ""

        cache_key = self._cache_key(location, event_dt)
        cached = self._cache.get(cache_key)
        if cached and cached.get("weather_text") and self._is_cache_valid(cached):
            return cached["weather_text"]

        try:
            async with aiohttp.ClientSession() as session:
                # Геокод
                geo_url = "http://api.openweathermap.org/geo/1.0/direct"
                geo_params = {"q": location, "limit": 1, "appid": self.api_key}
                async with session.get(geo_url, params=geo_params, timeout=15) as resp:
                    geo_data = await resp.json()
                    if not geo_data:
                        self._cache[cache_key] = {"weather_text": "", "timestamp": now_tz().isoformat(), "ttl": WEATHER_TTL_FAILURE}
                        self._save_cache()
                        return ""
                    lat, lon = geo_data[0]["lat"], geo_data[0]["lon"]

                # Прогноз
                weather_url = "https://api.openweathermap.org/data/2.5/forecast"
                params = {"lat": lat, "lon": lon, "appid": self.api_key, "units": "metric", "lang": "ru"}
                async with session.get(weather_url, params=params, timeout=15) as wresp:
                    weather_data = await wresp.json()

                # Найти ближайший прогноз
                candidates = []
                for item in weather_data.get("list", []):
                    ft = datetime.fromtimestamp(item["dt"], tz=LOCAL_TZ)
                    if ft.date() == event_dt.date():
                        candidates.append((abs((ft - event_dt).total_seconds()), item, ft))
                if not candidates:
                    self._cache[cache_key] = {"weather_text": "", "timestamp": now_tz().isoformat(), "ttl": WEATHER_TTL_FAILURE}
                    self._save_cache()
                    return ""
                _, best, best_time = min(candidates, key=lambda x: x[0])
                weather_desc = best["weather"][0]["description"].capitalize()
                temp = round(best["main"]["temp"])
                feels_like = round(best["main"].get("feels_like", temp))
                humidity = best["main"].get("humidity", "-")
                wind_speed = best.get("wind", {}).get("speed", "-")

                text = f"🌤️ <b>Погода ({best_time.strftime('%H:%M')}):</b> {weather_desc}\n🌡️ {temp}°C (ощущается как {feels_like}°C)\n💨 {wind_speed} м/с\n💧 {humidity}%"
                self._cache[cache_key] = {"weather_text": text, "timestamp": now_tz().isoformat(), "ttl": WEATHER_TTL_SUCCESS}
                self._save_cache()
                return text
        except Exception:
            self._cache[cache_key] = {"weather_text": "", "timestamp": now_tz().isoformat(), "ttl": WEATHER_TTL_FAILURE}
            self._save_cache()
            return ""

# ----------------------------
# ReminderService
# ----------------------------
class ReminderService:
    def __init__(self, bot: Bot, weather_service: WeatherService):
        self.bot = bot
        self.weather = weather_service
        self.sent_cache = DataStorage.load_json(SENT_CACHE_FILE) or {}
        self.reminders = {
            "5d": {"target": timedelta(days=5), "before": 12*3600, "after": 12*3600,
                   "template": "🏁 <b>Гонка приближается!</b>\nДо старта <b>{name}</b> осталось 5 дней!\n📅 {date}\n📍 {location}\n{weather}"},
            "3d": {"target": timedelta(days=3), "before": 6*3600, "after": 6*3600,
                   "template": "⚡ <b>Скоро старт!</b>\nДо гонки <b>{name}</b> осталось 3 дня!\n📅 {date}\n⏰ {time}\n📍 {location}\n{weather}"},
            "1d": {"target": timedelta(days=1), "before": 3*3600, "after": 3*3600,
                   "template": "🚀 <b>Завтра старт!</b>\nГонка <b>{name}</b> начинается завтра!\n📅 {date} {time}\n📍 {location}\n{weather}"},
            "2h": {"target": timedelta(hours=2), "before": 15*60, "after": 15*60,
                   "template": "⏰ <b>Старт через 2 часа!</b>\n<b>{name}</b> уже совсем скоро!\n📍 {location}\n⏰ {time}\n{weather}"}
        }

    def _has_sent(self, user_id: str, race_id: str, key: str) -> bool:
        return self.sent_cache.get(user_id, {}).get(f"{race_id}_{key}", False)

    def _mark_sent(self, user_id: str, race_id: str, key: str) -> None:
        self.sent_cache.setdefault(user_id, {})[f"{race_id}_{key}"] = True
        DataStorage.save_json(SENT_CACHE_FILE, self.sent_cache)

    async def _send_message(self, user_id: str, text: str):
        try:
            await self.bot.send_message(int(user_id), text, parse_mode="HTML", disable_web_page_preview=False)
            logging.info(f"Sent reminder to {user_id}")
        except Exception as e:
            logging.exception(f"Failed to send reminder to {user_id}: {e}")

    async def check_and_send(self):
        all_data = DataStorage.load_json(RACES_FILE)
        user_events = DataStorage.load_json(USER_EVENTS_FILE) or {}
        if not all_data or "categories" not in all_data:
            return

        all_races = []
        for cat in all_data.get("categories", []):
            for r in cat.get("races", []):
                rr = r.copy()
                rr["category_type"] = cat.get("type", "")
                all_races.append(rr)
        races_by_id = {str(r["id"]): r for r in all_races if "id" in r}

        now = now_tz()
        for user_id, race_ids in user_events.items():
            for race_id in race_ids:
                race = races_by_id.get(str(race_id))
                if not race: continue
                race_name, race_date, race_time = race.get("name",""), race.get("date",""), race.get("time","00:00")
                location, race_type = race.get("location",""), race.get("category_type","")
                event_dt = parse_event_datetime(race_date, race_time)
                if not event_dt or event_dt < now - timedelta(minutes=1): continue
                delta_sec = (event_dt - now).total_seconds()

                for key, cfg in self.reminders.items():
                    lower, upper = cfg["target"].total_seconds()-cfg["before"], cfg["target"].total_seconds()+cfg["after"]
                    if lower <= delta_sec <= upper and not self._has_sent(str(user_id), str(race_id), key):
                        weather_text = await self.weather.get_weather(location, event_dt, race_type) if location and key!="5d" else ""
                        if not weather_text:
                            if race_type=="trek": weather_text="🌤️ На велотреке обычно комфортно, +22°C"
                            elif key=="5d": weather_text="🌤️ Следи за прогнозом ближе к гонке."
                            else: weather_text="🌤️ Прогноз погоды временно недоступен."
                        msg = cfg["template"].format(name=race_name, date=event_dt.strftime("%d.%m.%Y"),
                                                     time=event_dt.strftime("%H:%M"), location=location, weather=weather_text)
                        race_url = race.get("url") or race.get("link")
                        if race_url: msg += f"\n\n👉 <a href='{race_url}'>Подробнее</a>"
                        await self._send_message(user_id, msg)
                        self._mark_sent(str(user_id), str(race_id), key)

# ----------------------------
# Setup
# ----------------------------
_weather_service: Optional[WeatherService] = None
_reminder_service: Optional[ReminderService] = None

def setup_reminders(bot: Bot, api_key: str = WEATHER_API_KEY, cron_expr: str = CRON_EXPR):
    global _weather_service, _reminder_service
    _weather_service = WeatherService(api_key)
    _reminder_service = ReminderService(bot, _weather_service)

    @aiocron.crontab(cron_expr)
    async def _cron_job():
        try:
            await _reminder_service.check_and_send()
        except Exception:
            logging.exception("Error in scheduled reminder job")

    logging.info(f"Reminders set up (cron: {cron_expr})")
