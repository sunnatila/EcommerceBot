from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, KeyboardButton

from loader import db

admin_button = ReplyKeyboardBuilder(
    markup=[
        [
            KeyboardButton(text="🎞 Filmlar bo'limi"),
            KeyboardButton(text="👤 Adminlar bo'limi"),
            KeyboardButton(text="👤 Foydalanuvchilar bo'limi"),
            KeyboardButton(text="🎞 Videolar bo'limi"),
            KeyboardButton(text="📊 Start bosganlar")
        ]
    ]
).adjust(2).as_markup(resize_keyboard=True)


admin_video_buttons = ReplyKeyboardBuilder(
    markup=[
        [
            KeyboardButton(text="🎥 Video yuborish"),
            KeyboardButton(text="🎞 Video qo'shish"),
            KeyboardButton(text="🎞 Videolar ro'yxati"),
            KeyboardButton(text="🔙 Ortga")
        ]
    ]
).adjust(2).as_markup(resize_keyboard=True)


admin_film_buttons = ReplyKeyboardBuilder(
    markup = [
        [
            KeyboardButton(text="🎞 Film qo'shish"),
            KeyboardButton(text="🎞 Filmlar ro'yxati"),
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


