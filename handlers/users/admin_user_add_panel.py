from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.default import admin_button
from .start import AdminFilter
from keyboards.inline import get_users_panel_buttons
from loader import db, dp


@dp.message(AdminFilter(), lambda msg: msg.text == "👤 Foydalanuvchilar bo'limi")
async def send_users_panel(msg: Message, state: FSMContext):
    await msg.answer("Foydalanuvchilar bo'limidan kerak bo'lgan tugmachani bo'sing:", reply_markup=get_users_panel_buttons)



@dp.callback_query(AdminFilter(), lambda call: call.data == 'back')
async def back_to_menu(call: CallbackQuery):
    await call.message.delete()
    await call.message.answer("Iltimos, kerakli kategoriyani tanlang 😊", reply_markup=admin_button)

