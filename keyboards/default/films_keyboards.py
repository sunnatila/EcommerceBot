from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from loader import db


async def get_active_products():
    products = await db.get_active_products()

    keyboard = []

    keyboard.append([KeyboardButton(text="🎁 Chegirma bilan olish")])


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
        resize_keyboard=True
    )
