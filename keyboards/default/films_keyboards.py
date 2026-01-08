from aiogram.utils.keyboard import KeyboardButton, ReplyKeyboardBuilder
from loader import db


async def get_active_products():
    products = await db.get_active_products()
    data = ReplyKeyboardBuilder()
    for product in products:
        data.add(KeyboardButton(text=f"{product[1]}"))

    data.add(KeyboardButton(text="🔙 Ortga"))
    return data.adjust(2).as_markup(resize_keyboard=True, one_time_keyboard=True)
