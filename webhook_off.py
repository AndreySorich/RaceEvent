from aiogram import Bot
import asyncio

API_TOKEN = "8432313674:AAF60FZ7wzrjTK4j3necHE-i7RWFK1CrOeE"

async def main():
    bot = Bot(token=API_TOKEN)
    await bot.delete_webhook()
    print("Webhook удалён!")
    await bot.session.close()

asyncio.run(main())




from aiogram import Bot, Dispatcher
from aiogram.types import Message
import asyncio

API_TOKEN = "8432313674:AAF60FZ7wzrjTK4j3necHE-i7RWFK1CrOeE"

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

@dp.message()
async def echo(message: Message):
    await message.answer(message.text)

async def main():
    await dp.start_polling()

asyncio.run(main())