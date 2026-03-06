from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🚴 Гонки на шоссе", callback_data="road")],
        [InlineKeyboardButton(text="🏟️ Гонки на треке", callback_data="track")],
        [InlineKeyboardButton(text="🏊‍♂️ Триатлон", callback_data="triathlon")],
        [InlineKeyboardButton(text="⭐ Мои старты", callback_data="my_events")],
        [InlineKeyboardButton(text="📅 Ближайшие гонки", callback_data="upcoming")],
        [InlineKeyboardButton(text="📞 Контакты", callback_data="contacts")]
    ])
