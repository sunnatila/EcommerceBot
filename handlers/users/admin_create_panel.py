from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.inline import send_admins_buttons, admin_settings_button
from .start import AdminFilter
from keyboards.default import admin_create_buttons, admin_button
from loader import db, dp


@dp.message(lambda msg: msg.text == "👤 Adminlar bo'limi")
async def send_admin_panel(msg: Message, state: FSMContext):
    await msg.answer("Guruhlar bo'limida kerak bo'lgan tugmachani bo'sing.", reply_markup=admin_create_buttons)


@dp.message(AdminFilter(), lambda msg: msg.text == "🔙 Ortga")
async def admin_panel(msg: Message, state: FSMContext):
    await msg.answer("Iltimos, kerakli kategoriyani tanlang 😊", reply_markup=admin_button)
    await state.clear()


@dp.message(AdminFilter(), lambda msg: msg.text == "👤 Admin qo'shish")
async def admin_create(msg: Message, state: FSMContext):
    admin = await db.get_admins()
    if admin:
        await msg.answer("Admin allaqahon yaratilgan!\n"
                         "Admin qo'shish uchun oldin o'chirib tashlang yoki o'zgartiring.",
                         reply_markup=admin_create_buttons)
        await state.clear()
        return
    await msg.answer("Adminning username ni kiriting:")
    await state.set_state("get_admin_username")


@dp.message(AdminFilter(), StateFilter("get_admin_username"))
async def get_admin_username(msg: Message, state: FSMContext):
    username = msg.text
    data = await state.get_data()
    admin_id = data.get("admin_id")
    print(admin_id)
    if admin_id:
        await db.update_admin_info(admin_id, username)
        await msg.answer("Admin muvaffaqiyatli tarzda o'zgartirildi.", reply_markup=admin_create_buttons)
    else:
        await db.add_admin(username)
        await msg.answer("Admin muvaffaqiyatli tarzda qo'shildi.", reply_markup=admin_create_buttons)
    await state.clear()


@dp.message(AdminFilter(), lambda msg: msg.text == "👤 Adminlar ro'yxati")
async def send_admins(msg: Message, state: FSMContext):
    await msg.answer("Ko'rmoqchi bo'lgan admini tanlang:", reply_markup=await send_admins_buttons())
    await state.set_state("get_admin_id")


@dp.callback_query(AdminFilter(), StateFilter("get_admin_id"), lambda call: call.data == "back")
async def back_func(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer("Adminlar bo'limi", reply_markup=admin_create_buttons)
    await state.clear()


@dp.callback_query(AdminFilter(), StateFilter("get_admin_id"), lambda call: call.data.isdigit())
async def back_func(call: CallbackQuery, state: FSMContext):
    admin_id = call.data[0]
    await call.message.delete()
    data = await db.get_admin_by_id(admin_id)
    await state.update_data({"admin_id": data[0]})
    info = f"Username: {data[1]}"
    await call.message.answer(info, reply_markup=admin_settings_button)
    await state.set_state("get_admin_info")


@dp.callback_query(AdminFilter(), StateFilter("get_admin_info"))
async def get_admin_info(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    data = await state.get_data()
    if call.data == "edit":
        await admin_edit_func(call, state)
    elif call.data == "delete":
        await db.delete_admin(data.get("admin_id"))
        await call.message.answer("Admin muvaffaqiyatli tarzda o'chirildi.", reply_markup=admin_create_buttons)
        await state.clear()
    elif call.data == "back":
        await call.message.answer("Qaysi admin ma'lumotini kormoqchisiz?", reply_markup=await send_admins_buttons())
        await state.set_state("get_admin_id")


async def admin_edit_func(call, state):
    await call.message.answer("Adminning username ni kiriting:")
    await state.set_state("get_admin_username")

