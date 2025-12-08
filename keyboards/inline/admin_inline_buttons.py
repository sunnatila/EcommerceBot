from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton

from loader import db

group_active_button = InlineKeyboardBuilder(
    markup=[
        [
            InlineKeyboardButton(text="Ha aktiv", callback_data="active"),
            InlineKeyboardButton(text="Yo'q", callback_data="not_active")
        ]
    ]
).adjust(2).as_markup()


admin_group_save_buttons = InlineKeyboardBuilder(
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
    for group in groups:
        groups_info_button.add(InlineKeyboardButton(text=f"{group[1]}", callback_data=f"{group[0]}"))

    groups_info_button.add(InlineKeyboardButton(text="🔙 Qaytish", callback_data="back"))
    return groups_info_button.adjust(3).as_markup()


group_settings_button = InlineKeyboardBuilder(
    markup=[
        [
            InlineKeyboardButton(text="✏️Tahrirlash", callback_data="edit"),
            InlineKeyboardButton(text="🗑️ O'chirish", callback_data="delete"),
            InlineKeyboardButton(text="🔙 Qaytish", callback_data="back"),
        ]
    ]
).adjust(2).as_markup()

