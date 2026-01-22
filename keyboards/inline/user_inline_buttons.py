from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from loader import db

async def user_product_buttons(pr_id):
    buttons = InlineKeyboardBuilder(
        markup=[
            [
                InlineKeyboardButton(text="Sotib olish", callback_data=f"product_buy_{pr_id}"),
                InlineKeyboardButton(text="Sovgʻa qilish🎁", callback_data="present_product"),
            ]
        ]
    ).adjust(2).as_markup()
    return buttons


async def all_pr_buy_buttons():
    buttons = InlineKeyboardBuilder(
        markup=[
            [
                InlineKeyboardButton(text="Sotib olish", callback_data=f"all_product_buy"),
            ]
        ]
    ).adjust(1).as_markup()
    return buttons


user_payment_chooser_button = InlineKeyboardBuilder(
    markup=[
        [
            InlineKeyboardButton(text="💳 Click", callback_data="click"),
            InlineKeyboardButton(text="💳 PayMe", callback_data="payme"),
            InlineKeyboardButton(text="Boshqa to'lov usuli", callback_data="other_payment"),
        ]
    ]
).adjust(2).as_markup()


all_product_payment_chooser_button = InlineKeyboardBuilder(
    markup=[
        [
            InlineKeyboardButton(text="💳 Click", callback_data="all_product_click"),
            InlineKeyboardButton(text="💳 PayMe", callback_data="all_product_payme"),
            InlineKeyboardButton(text="Boshqa to'lov usuli", callback_data="all_product_other_payment"),
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



async def sent_payment_url(data: dict):
    from product.views import send_link_for_payment
    result = await send_link_for_payment(data)
    payment_url = result.get('payment_url')
    button = InlineKeyboardBuilder(
        markup=[
            [
                InlineKeyboardButton(text="Sotib olish", url=payment_url)
            ]
        ]
    ).adjust(1).as_markup()
    return button
