from aiogram import Bot
import asyncio

BOT_TOKEN = "8432313674:AAF60FZ7wzrjTK4j3necHE-i7RWFK1CrOeE"

async def clear_menu():
    bot = Bot(token=BOT_TOKEN)
    await bot.delete_my_commands()
    print("✅ Старое меню удалено.")

asyncio.run(clear_menu())