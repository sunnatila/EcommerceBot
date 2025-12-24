from aiogram.utils.keyboard import ReplyKeyboardBuilder, KeyboardButton


user_buttons = ReplyKeyboardBuilder(
    markup=[
        [
            KeyboardButton(text="🎬 Filmlar bo'limi"),
            KeyboardButton(text="🎞 Mening Filmlarim"),
            KeyboardButton(text="🎥 Bonus filmlar"),
            KeyboardButton(text="👤 Admin bilan bog'lanish"),
        ]
    ]
).adjust(2).as_markup(resize_keyboard=True, one_time_keyboard=True)

contact_button = ReplyKeyboardBuilder(
    markup=[
        [
            KeyboardButton(text="📞 Kontaktni ulashish", request_contact=True)
        ]
    ]
).adjust(1).as_markup(resize_keyboard=True, one_time_keyboard=True)
