from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, KeyboardButton

from loader import db

admin_button = ReplyKeyboardBuilder(
    markup=[
        [
            KeyboardButton(text="📋 Guruhlar bo'limi"),
            KeyboardButton(text="👤 Adminlar bo'limi"),
            KeyboardButton(text="👤 Foydalanuvchilar bo'limi"),
        ]
    ]
).adjust(2).as_markup(resize_keyboard=True)


admin_group_buttons = ReplyKeyboardBuilder(
    markup = [
        [
            KeyboardButton(text="📋 Guruh qo'shish"),
            KeyboardButton(text="📋 Guruhlar ro'yxati"),
            KeyboardButton(text="🔙 Ortga")
        ]
    ]
).adjust(2).as_markup(resize_keyboard=True)

admin_create_buttons = ReplyKeyboardBuilder(
    markup = [
        [
            KeyboardButton(text="👤 Admin qo'shish"),
            KeyboardButton(text="👤 Adminlar ro'yxati"),
            KeyboardButton(text="🔙 Ortga")
        ]
    ]
).adjust(2).as_markup(resize_keyboard=True)


get_users_panel_buttons = ReplyKeyboardBuilder(
    markup=[
        [
            KeyboardButton(text="👤 Foydalanuvchiga film qo'shish"),
            KeyboardButton(text="🔙 Ortga"),
        ]
    ]
).adjust(2).as_markup(resize_keyboard=True)


async def get_products_for_admin():
    products = await db.get_active_products()
    keyboard = []

    keyboard.append([KeyboardButton(text="Hamma filmlarga ruxsat berish")])

    row = []
    for i, product in enumerate(products, start=1):
        row.append(KeyboardButton(text=product[1]))
        if i % 2 == 0:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)

    keyboard.append([KeyboardButton(text="🔙 Ortga")])

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
    )


