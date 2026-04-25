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


def video_settings_button(video_id):
    return InlineKeyboardBuilder(
        markup=[
            [
                InlineKeyboardButton(text="✏️Tahrirlash", callback_data=f"video_edit:{video_id}"),
                InlineKeyboardButton(text="🗑️ O'chirish", callback_data=f"video_delete:{video_id}"),
            ]
        ]
    ).adjust(2).as_markup()


_film_edit_builder = InlineKeyboardBuilder()
_film_edit_builder.button(text="🔄 To'liq tahrirlash", callback_data="edit_full")
_film_edit_builder.button(text="🎬 Nomi", callback_data="edit_title")
_film_edit_builder.button(text="📝 Tavsif", callback_data="edit_description")
_film_edit_builder.button(text="📺 1080p narxi", callback_data="edit_price_1080p")
_film_edit_builder.button(text="🔗 1080p link", callback_data="edit_group_url_1080p")
_film_edit_builder.button(text="📺 4K narxi", callback_data="edit_price_4k")
_film_edit_builder.button(text="🔗 4K link", callback_data="edit_group_url_4k")
_film_edit_builder.button(text="🎥 Video", callback_data="edit_video_url")
_film_edit_builder.button(text="⚙️ Holat", callback_data="edit_is_active")
_film_edit_builder.button(text="🔢 Tartib", callback_data="edit_position")
_film_edit_builder.button(text="🔙 Ortga", callback_data="edit_back")
_film_edit_builder.adjust(1, 2, 2, 2, 2, 1, 1)
film_edit_fields_button = _film_edit_builder.as_markup()


product_paid_button = InlineKeyboardBuilder(
    markup=[
        [
            InlineKeyboardButton(text="Bepul", callback_data="free"),
            InlineKeyboardButton(text="Pullik", callback_data="paid"),
        ]
    ]
).adjust(2).as_markup()



async def resolution_buttons_for_admin():
    buttons = InlineKeyboardBuilder(
    markup=[
        [
            InlineKeyboardButton(text="📺 1080p", callback_data=f"res_1080p"),
            InlineKeyboardButton(text="📺 4K", callback_data=f"res_4k"),
        ]
    ]
    ).adjust(2).as_markup()
    return buttons



