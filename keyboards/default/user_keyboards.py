from aiogram.utils.keyboard import ReplyKeyboardBuilder, KeyboardButton

from loader import db

user_buttons = ReplyKeyboardBuilder(
    markup=[
        [
            KeyboardButton(text="🎬 Filmlar bo'limi"),
            KeyboardButton(text="🎞 Mening Filmlarim"),
            KeyboardButton(text="🎥 Bonus filmlar"),
            KeyboardButton(text="👤 Admin bilan bog'lanish"),
        ]
    ]
).adjust(2).as_markup(resize_keyboard=True)

contact_button = ReplyKeyboardBuilder(
    markup=[
        [KeyboardButton(text="📞 Kontaktni ulashish", request_contact=True)]
    ]
).adjust(1).as_markup(resize_keyboard=True)


async def user_orders_keyboard(unique_films):
    """Foydalanuvchining sotib olgan unikal filmlari (resolution'siz)"""
    keyboard = ReplyKeyboardBuilder()

    for film in unique_films:
        # film: (product_id, title)
        keyboard.add(KeyboardButton(text=film[1]))

    keyboard.add(KeyboardButton(text="🔙 Ortga"))
    return keyboard.adjust(2).as_markup(resize_keyboard=True)


async def get_free_films():
    data = await db.get_free_products()
    films = ReplyKeyboardBuilder()

    if data:
        for film in data:
            films.add(KeyboardButton(text=f"{film[1]}"))

    films.add(KeyboardButton(text="🔙 Ortga"))
    return films.adjust(2).as_markup(resize_keyboard=True)


back_button = ReplyKeyboardBuilder(
    markup=[
        [KeyboardButton(text="🔙 Ortga")]
    ]
).adjust(1).as_markup(resize_keyboard=True)