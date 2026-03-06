from aiogram import Bot
from aiogram.types import BotCommand

async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="🏁 Главное меню"),
        BotCommand(command="my", description="🚴 Мои старты"),
        BotCommand(command="races", description="📅 Список гонок"),
        BotCommand(command="contacts", description="📞 Контакты"),
        BotCommand(command="help", description="ℹ️ Помощь"),
    ]
    await bot.set_my_commands(commands)
