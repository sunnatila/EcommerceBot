from aiogram.types import Message, CallbackQuery
from loader import db, dp


@dp.message(lambda msg: msg.text == "👤 Admin bilan bog'lanish")
async def send_admin_contact(msg: Message):
    admin_data = await db.get_admins()
    if admin_data:
        username = admin_data[0][1]
    else:
        username = "@NodirNazirovv"
    await msg.answer(f"Adminga bog'lanish uchun {username} ga yozing!")

