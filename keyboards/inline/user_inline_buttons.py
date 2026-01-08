from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from loader import db

user_product_buttons = InlineKeyboardBuilder(
    markup=[
        [
            InlineKeyboardButton(text="Sotib olish", callback_data="product_buy"),
            InlineKeyboardButton(text="Yaqinimga sovg'a qilish 🎁", callback_data="present_product"),
            InlineKeyboardButton(text="🔙 Ortga", callback_data="back"),
        ]
    ]
).adjust(2).as_markup()


user_payment_chooser_button = InlineKeyboardBuilder(
    markup=[
        [
            InlineKeyboardButton(text="💳 Click", callback_data="click"),
            InlineKeyboardButton(text="💳 PayMe", callback_data="payme"),
        ]
    ]
).adjust(2).as_markup()


async def user_orders(user_id):
    user_paid_orders = await db.get_user_paid_orders(user_id)
    orders_button = InlineKeyboardBuilder()
    if user_paid_orders:
        for order in user_paid_orders:
            orders_button.add(InlineKeyboardButton(text=f"{order[1]}", callback_data=f"{order[0]}"))
    orders_button.add(InlineKeyboardButton(text="🔙 Ortga", callback_data="back"))

    return orders_button.adjust(2).as_markup()


async def back_button(link):
    button = InlineKeyboardBuilder(
        markup=[
            [
                InlineKeyboardButton(text="Guruhga qo'shilish", url=link),
                InlineKeyboardButton(text="🔙 Ortga", callback_data="back")
            ]
        ]
    ).adjust(1).as_markup()
    return button


async def get_free_films():
    data = await db.get_free_products()
    films = InlineKeyboardBuilder()
    if data:
        for film in data:
            films.add(InlineKeyboardButton(text=f"{film[1]}", callback_data=f"{film[0]}"))

    films.add(InlineKeyboardButton(text="🔙 Ortga", callback_data="back"))
    return films.adjust(2).as_markup()

