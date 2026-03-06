from aiogram import Bot
import asyncio

API_TOKEN = "8432313674:AAF60FZ7wzrjTK4j3necHE-i7RWFK1CrOeE"
WEBHOOK_URL = "https://your-domain.com/webhook"  # ← сюда Telegram будет слать апдейты

async def main():
    await bot.set_webhook(WEBHOOK_URL)
    info = await bot.get_webhook_info()
    print("Webhook установлен:", info.url)
    await bot.session.close()

asyncio.run(main())