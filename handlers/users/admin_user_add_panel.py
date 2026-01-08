from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from .start import AdminFilter
from keyboards.inline import get_users_panel_buttons
from loader import db, dp


@dp.message(AdminFilter(), lambda msg: msg.text == "👤 Foydalanuvchilar bo'limi")
async def send_users_panel(msg: Message):
    await msg.answer("Foydalanuvchilar bo'limidan kerak bo'lgan tugmachani bo'sing:", reply_markup=get_users_panel_buttons)
