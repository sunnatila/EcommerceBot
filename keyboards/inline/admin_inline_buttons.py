from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton


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
