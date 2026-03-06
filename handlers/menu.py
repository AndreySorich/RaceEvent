from aiogram import Router, types
from keyboards.main_menu import main_menu

router = Router()

@router.callback_query(lambda c: c.data == "road")
async def show_road(callback: types.CallbackQuery):
    await callback.message.edit_text("🚴 Список шоссейных гонок:", reply_markup=main_menu())
