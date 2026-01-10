from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from loader import db

async def user_product_buttons(pr_id):
    buttons = InlineKeyboardBuilder(
        markup=[
            [
                InlineKeyboardButton(text="Sotib olish", callback_data=f"product_buy_{pr_id}"),
                InlineKeyboardButton(text="Yaqinimga sovg'a qilish 🎁", callback_data="present_product"),
            ]
        ]
    ).adjust(2).as_markup()
    return buttons


user_payment_chooser_button = InlineKeyboardBuilder(
    markup=[
        [
            InlineKeyboardButton(text="💳 Click", callback_data="click"),
            InlineKeyboardButton(text="💳 PayMe", callback_data="payme"),
        ]
    ]
).adjust(2).as_markup()



async def group_link_button(link):
    button = InlineKeyboardBuilder(
        markup=[
            [
                InlineKeyboardButton(text="Guruhga qo'shilish", url=link)
            ]
        ]
    ).adjust(1).as_markup()
    return button


