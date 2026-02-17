from aiogram import types
from aiogram.filters import CommandStart, BaseFilter, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

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
    user_status = await db.is_started(message.from_user.id)
    if not user_status:
        await db.add_bot_start(
            message.from_user.id,
            message.from_user.full_name,
            message.from_user.username
        )
    data = await db.get_user_by_tg_id(message.from_user.id)
    if data:
        await message.answer("Kerakli bo'limni tanlang 😊", reply_markup=user_buttons)
        return

    await message.answer(
        "Assalomu alaykum!\n"
        "PhD TV ga xush kelibsiz 😊\n\n"
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
    user_data = await db.get_user_by_phone(phone_number)
    await state.clear()
    video_data = await db.get_videos()
    if user_data and user_data[2] is None:
        await db.update_user(fullname, phone_number, msg.from_user.id)
        await _send_success_message(msg, user_buttons, video_data)


    elif user_data and user_data[2]:
        await msg.answer(
            "Bu raqamga tegishli foydalanuvchi mavjud 😊"
        )

    else:
        await db.add_user(fullname, phone_number, msg.from_user.id)
        await _send_success_message(msg, user_buttons, video_data)


@dp.message(StateFilter("get_phone_number"))
async def get_phone_number_text(msg: types.Message, state: FSMContext):
    data = await state.get_data()
    await state.clear()

    phone_number = msg.text.strip()

    if not _is_valid_phone(phone_number):
        await msg.answer(
            "❌ Telefon raqam noto'g'ri kiritildi.\n"
            "Iltimos, telefon raqamingizni qaytadan kiriting (namuna: +99890xxxxxxx yoki 90xxxxxxx).\n"
            "Yoki pastdagi tugmachani bosing 👇",
            reply_markup=contact_button
        )
        return

    if phone_number.isdigit() and len(phone_number) == 9:
        phone_number = '+998' + phone_number

    fullname = data.get("fullname")
    user_data = await db.get_user_by_phone(phone_number)
    video_data = await db.get_videos()


    if user_data and user_data[2] is None:
        await db.update_user(fullname, phone_number, msg.from_user.id)
        await _send_success_message(msg, user_buttons, video_data)

    elif user_data and user_data[2]:
        await msg.answer(
            "Bu raqamga tegishli foydalanuvchi mavjud 😊",
            reply_markup=ReplyKeyboardRemove()
        )

    else:
        await db.add_user(fullname, phone_number, msg.from_user.id)
        await _send_success_message(msg, user_buttons, video_data)


def _is_valid_phone(phone_number: str) -> bool:
    if phone_number.startswith('+998') and phone_number[4:].isdigit() and len(phone_number) == 13:
        return True
    elif phone_number.isdigit() and len(phone_number) == 9:
        return True
    return False


async def _send_success_message(msg: types.Message, keyboard, video_data: list):
    await msg.answer(
        "Tabriklaymiz! Ro'yxatdan muvaffaqiyatli o'tdingiz ✅\n"
        "Endi botdan to'liq tarzda foydalanishingiz mumkin.\n\n"
        "Kerakli bo'limni tanlang 😊",
        reply_markup=keyboard
    )

    if video_data:
        video_url = video_data[0][1]
        video_desc = video_data[0][2]
        await msg.answer_video(
            video=video_url,
            caption=video_desc,
            parse_mode='HTML'
        )
