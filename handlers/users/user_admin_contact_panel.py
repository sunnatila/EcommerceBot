from aiogram.types import Message, CallbackQuery
from loader import db, dp


@dp.message(lambda msg: msg.text == "👤 Admin bilan bog'lanish")
async def send_admin_contact(msg: Message):
    admin_data = await db.get_admins()
    if admin_data:
        username = admin_data[0][1]
    else:
        username = "@phd_tv_admin"
    await msg.answer(
        f"Agar savollaringiz yoki yordam kerak bo‘lsa,"
             f" admin bilan bog‘lanishingiz mumkin: <b>{username}</b>",
        parse_mode="HTML"
    )

