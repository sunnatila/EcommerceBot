from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from loader import db

film_active_button = InlineKeyboardBuilder(
    markup=[
        [
            InlineKeyboardButton(text="Ha aktiv", callback_data="active"),
            InlineKeyboardButton(text="Yo'q", callback_data="not_active")
        ]
    ]
).adjust(2).as_markup()


admin_film_save_buttons = InlineKeyboardBuilder(
    markup=[
        [
            InlineKeyboardButton(text="💾 Saqlash", callback_data="save"),
            InlineKeyboardButton(text="✏️ Tahrirlash", callback_data="edit"),
            InlineKeyboardButton(text="❌ Rad etish", callback_data="not save")
        ]
    ]
).adjust(2).as_markup()



async def get_product_list():
    groups = await db.get_products()
    groups_info_button = InlineKeyboardBuilder()
    if groups:
        for group in groups:
            groups_info_button.add(InlineKeyboardButton(text=f"{group[1]}", callback_data=f"{group[0]}"))

    groups_info_button.add(InlineKeyboardButton(text="🔙 Ortga", callback_data="back"))
    return groups_info_button.adjust(2).as_markup()


film_settings_button = InlineKeyboardBuilder(
    markup=[
        [
            InlineKeyboardButton(text="✏️Tahrirlash", callback_data="edit"),
            InlineKeyboardButton(text="🗑️ O'chirish", callback_data="delete"),
            InlineKeyboardButton(text="🔙 Ortga", callback_data="back"),
        ]
    ]
).adjust(2).as_markup()


async def send_admins_buttons():
    admins = await db.get_admins()
    admin_buttons = InlineKeyboardBuilder()
    for admin in admins:
        admin_buttons.add(InlineKeyboardButton(text=f"{admin[1]}", callback_data=f"{admin[0]}"))

    admin_buttons.add(InlineKeyboardButton(text="🔙 Ortga", callback_data="back"))

    return admin_buttons.adjust(1).as_markup()


admin_settings_button = InlineKeyboardBuilder(
    markup=[
        [
            InlineKeyboardButton(text="✏️Tahrirlash", callback_data="edit"),
            InlineKeyboardButton(text="🗑️ O'chirish", callback_data="delete"),
            InlineKeyboardButton(text="🔙 Ortga", callback_data="back"),
        ]
    ]
).adjust(2).as_markup()


product_paid_button = InlineKeyboardBuilder(
    markup=[
        [
            InlineKeyboardButton(text="Bepul", callback_data="free"),
            InlineKeyboardButton(text="Pullik", callback_data="paid"),
        ]
    ]
).adjust(2).as_markup()




