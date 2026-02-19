from aiogram import types
from aiogram.filters import CommandStart, BaseFilter
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
    user_status = await db.is_started(message.from_user.id)
    if not user_status:
        await db.add_bot_start(
            message.from_user.id,
            message.from_user.full_name,
            message.from_user.username
        )
    username = message.from_user.username
    user_data_from_tg_id = await db.get_user_by_tg_id(message.from_user.id)
    if username:
        if username.startswith("@"):
            pass
        else:
            username = "@" + username
        user_data_from_username = await db.get_user_by_username(username)

        if user_data_from_username:
            if not user_data_from_username[2]:
                await db.update_user(tg_id=message.from_user.id, fullname=message.from_user.full_name,
                                     username=username)
                await message.answer(
                    text="Assalomu alaykum!\n"
                         "PhD TV ga xush kelibsiz.\n"
                         "Kerakli bo'limni tanlang 😊\n",
                    reply_markup=user_buttons
                )

            else:
                await message.answer("Kerakli bo'limni tanlang 😊", reply_markup=user_buttons)

        elif user_data_from_tg_id:
            if not user_data_from_tg_id[2]:
                await db.update_user_by_tg_id(tg_id=message.from_user.id, fullname=message.from_user.full_name, username=username)
                await message.answer(
                    text="Kerakli bo'limni tanlang 😊",
                    reply_markup=user_buttons
                )

            else:
                await message.answer("Kerakli bo'limni tanlang 😊", reply_markup=user_buttons)

        else:
            await db.add_user(tg_id=message.from_user.id, fullname=message.from_user.full_name, username=username)
            await message.answer(
                text="Assalomu alaykum!\n"
                     "PhD TV ga xush kelibsiz.\n"
                     "Kerakli bo'limni tanlang 😊\n",
                reply_markup=user_buttons
            )
    else:
        if user_data_from_tg_id:
            await message.answer("Kerakli bo'limni tanlang 😊", reply_markup=user_buttons)
            return
        await db.add_user(tg_id=message.from_user.id, fullname=message.from_user.full_name)
        await message.answer(
            text="Assalomu alaykum!\n"
                 "PhD TV ga xush kelibsiz.\n"
                 "Kerakli bo'limni tanlang 😊\n",
            reply_markup=user_buttons
        )
