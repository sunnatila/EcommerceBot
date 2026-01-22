from aiogram import types
from aiogram.filters import CommandStart, BaseFilter, StateFilter
from aiogram.fsm.context import FSMContext

from data.config import ADMINS
from keyboards.default import admin_button, user_buttons, contact_button
from loader import dp, db


class AdminFilter(BaseFilter):
    async def __call__(self, msg: types.Message,  *args, **kwargs):
        return str(msg.from_user.id) in ADMINS


@dp.message(AdminFilter(), CommandStart())
async def admin_start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Assalomu alaykum!\n"
        "Admin panelga xush kelibsiz 👋", reply_markup=admin_button
    )


@dp.message(CommandStart())
async def user_start(message: types.Message, state: FSMContext):
    data = await db.get_user_by_tg_id(message.from_user.id)
    if data:
        await message.answer("Kerakli bo'limni tanlang 😊", reply_markup=user_buttons)
        return
    await message.answer(
        "Assalomu alaykum!\n"
        "PhD TV botiga xush kelibsiz 🎬\n\n"
        "Botdan foydalanish uchun avval ro'yxatdan o'tishingiz kerak.\n"
        "Iltimos, to'liq ism-familiyangizni kiriting:"
    )
    await state.set_state("get_user_fullname")


@dp.message(StateFilter("get_user_fullname"))
async def get_user_fullname(msg: types.Message, state: FSMContext):
    await state.update_data({"fullname": msg.text})
    await msg.answer(
        "Endi telefon raqamingizni kiriting.\n"
        "Namuna: +99890xxxxxxx yoki 90xxxxxxx.\n"
        "Yoki pastdagi tugmachani bosing 👇", reply_markup=contact_button
    )
    await state.set_state("get_phone_number")


@dp.message(StateFilter("get_phone_number"), lambda msg: msg.contact is not None)
async def get_phone_number_contact(msg: types.Message, state: FSMContext):
    phone_number = msg.contact.phone_number
    data = await state.get_data()
    fullname = data.get("fullname")
    await db.add_user(fullname, phone_number, msg.from_user.id)
    await msg.answer(
        "Botdan muvaffaqiyatli tarzda foydalanishingiz mumkin.", reply_markup=user_buttons
    )
    await state.clear()


@dp.message(StateFilter("get_phone_number"))
async def get_phone_number_text(msg: types.Message, state: FSMContext):
    phone_number = msg.text.strip()
    if phone_number.startswith('+998') and phone_number[4:].isdigit() and len(phone_number) == 13:
        pass
    elif phone_number.isdigit() and len(phone_number) == 9:
        phone_number = '+998' + phone_number
    else:
        await msg.answer(
            "❌ Telefon raqam noto'g'ri kiritildi.\n"
            "Iltimos, telefon raqamingizni qaytadan kiriting (namuna: +99890xxxxxxx yoki 90xxxxxxx).\n"
            "Yoki pastdagi tugmachani bosing 👇", reply_markup=contact_button
        )
        return
    data = await state.get_data()
    fullname = data.get("fullname")
    await db.add_user(fullname, phone_number, msg.from_user.id)
    await msg.answer(
        "Tabriklaymiz! Ro'yxatdan muvaffaqiyatli o'tdingiz ✅\n"
        "Endi botdan to'liq tarzda foydalanishingiz mumkin.\n\n"
        "Kerakli bo'limni tanlang 😊", reply_markup=user_buttons
    )
    await state.clear()
