import json
import logging
from datetime import datetime
from pathlib import Path
from aiogram import BaseMiddleware
from aiogram.types import Message

USERS_FILE = Path("data/users.json")
USERS_FILE.parent.mkdir(exist_ok=True)


class UserLoggerMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()
        # Загружаем пользователей из файла, если он есть
        if USERS_FILE.exists():
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                try:
                    self.users = json.load(f)
                except json.JSONDecodeError:
                    self.users = {}
        else:
            self.users = {}

        # 🔄 Преобразуем старый формат {"id": "username"} → {"id": {"username": "...", "registered_at": "..."}}
        for uid, val in list(self.users.items()):
            if isinstance(val, str):
                self.users[uid] = {
                    "username": val,
                    "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                }

    async def __call__(self, handler, event: Message, data: dict):
        if not isinstance(event, Message) or not event.from_user:
            return await handler(event, data)

        user_id = str(event.from_user.id)
        username = event.from_user.username or "unknown"

        # Если нового пользователя нет — добавляем
        if user_id not in self.users:
            self.users[user_id] = {
                "username": username,
                "registered_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            logging.info(f"🆕 Новый пользователь: {user_id} ({username})")

        # Если есть, но username изменился — обновляем
        elif self.users[user_id]["username"] != username:
            old_name = self.users[user_id]["username"]
            self.users[user_id]["username"] = username
            logging.info(f"🔁 Пользователь {user_id} сменил имя: {old_name} → {username}")

        # Сохраняем изменения
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.users, f, ensure_ascii=False, indent=2)

        return await handler(event, data)
