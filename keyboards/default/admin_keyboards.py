from aiogram.utils.keyboard import ReplyKeyboardBuilder, KeyboardButton


admin_button = ReplyKeyboardBuilder(
    markup=[
        [
            KeyboardButton(text="📋 Guruhlar bo'limi")
        ]
    ]
).adjust(2).as_markup(one_time_keyboard=True, resize_keyboard=True)


admin_group_buttons = ReplyKeyboardBuilder(
    markup = [
        [
            KeyboardButton(text="📋 Guruh qo'shish"),
            KeyboardButton(text="📋 Guruhlar ro'yxati"),
            KeyboardButton(text="🔙 Qaytish")
        ]
    ]
).adjust(2).as_markup(resize_keyboard=True, one_time_keyboard=True)
