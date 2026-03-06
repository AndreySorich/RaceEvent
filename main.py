# main.py
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
import os
from dotenv import load_dotenv
from handlers import menu
import logging

load_dotenv()
bot = Bot(token=os.getenv("8432313674:AAF60FZ7wzrjTK4j3necHE-i7RWFK1CrOeE"))
dp = Dispatcher()
dp.include_router(menu.router)

@dp.message(Command("start"))
async def start(message: Message):
    await message.answer("Привет! 👋 Это Race Event — твой спортивный календарь.")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
