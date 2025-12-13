from typing import Union

from aiogram import types
from aiogram.enums import ContentType
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove, CallbackQuery

from keyboards.inline import group_active_button, admin_group_save_buttons, get_product_list, group_settings_button
from .start import AdminFilter
from keyboards.default import admin_group_buttons, admin_button
from loader import db, bot, dp
from states import GroupStates


@dp.message(AdminFilter(), lambda msg: msg.text == "📋 Guruhlar bo'limi")
async def group_panel(msg: types.Message):
    await msg.answer("Guruhlar bo'limida kerak bo'lgan tugmachani bo'sing.", reply_markup=admin_group_buttons)


# Create Group panel --------------------------------------------------------------------------------------



@dp.message(AdminFilter(), lambda msg: msg.text == "📋 Guruh qo'shish")
async def add_group(msg: Union[types.Message, CallbackQuery], state: FSMContext, pr_id=None):
    if isinstance(msg, CallbackQuery):
        await msg.message.answer("Guruh nomini kiriting:")
        await state.update_data({"product_id": pr_id})
    else:
        await msg.answer("Guruh nomini kiriting:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(GroupStates.group_name)


@dp.message(AdminFilter(), GroupStates.group_name, lambda msg: msg.content_type in [ContentType.TEXT])
async def get_group_name(msg: types.Message, state: FSMContext):
    await state.update_data({"group_name": msg.text})
    await msg.answer("Guruh haqida ma'lumot kiriting:")
    await state.set_state(GroupStates.group_description)


@dp.message(AdminFilter(), GroupStates.group_description, lambda msg: msg.content_type in [ContentType.TEXT])
async def get_group_description(msg: types.Message, state: FSMContext):
    await state.update_data({"group_description": msg.text})
    await msg.answer("Guruh narxini kiriting (so'mda): ")
    await state.set_state(GroupStates.group_price)


@dp.message(AdminFilter(), GroupStates.group_price)
async def get_group_price(msg: types.Message, state: FSMContext):
    price = msg.text
    if price.isdigit():
        await state.update_data({"group_price": int(price)})
        await msg.answer("Guruh linkini kiriting:")
        await state.set_state(GroupStates.group_url)
        return
    await msg.answer("Guruh narxini faqat raqamlarda kiring!!\n"
                     "Misol uchun: 25000")

@dp.message(AdminFilter(), GroupStates.group_url, lambda msg: msg.content_type in [ContentType.TEXT])
async def get_group_url(msg: types.Message, state: FSMContext):
    await state.update_data({"group_url": msg.text})
    await msg.answer("Guruh aktivmi?", reply_markup=group_active_button)
    await state.set_state(GroupStates.group_status)


@dp.callback_query(AdminFilter(), GroupStates.group_status)
async def get_group_status(call: CallbackQuery, state: FSMContext):
    await state.update_data({"group_status": call.data})
    await call.message.delete()
    await call.message.answer("Guruh haqida video tashlang:")
    await state.set_state(GroupStates.group_video)

@dp.message(AdminFilter(), GroupStates.group_video, lambda msg: msg.content_type in [ContentType.VIDEO])
async def get_group_image(msg: types.Message, state: FSMContext):
    video = msg.video.file_id
    await state.update_data({"group_video": video})
    await msg.delete()
    data = await state.get_data()
    info = "📋 <b>Guruh haqida ma'lumot:</b>\n"
    info += f"👥 <b>Guruhning nomi:</b> {data.get('group_name')}\n"
    info += f"📝 <b>Guruhning ma'lumoti:</b> {data.get('group_description')}\n"
    info += f"🔗 <b>Guruhning ssilkasi:</b> {data.get('group_url')}\n"
    info += f"⚙️ <b>Guruhning xolati:</b>  {'✅' if data.get('group_status') == 'active' else '❌'}\n"
    info += f"💰 <b>Guruhning narxi:</b> {data.get('group_price')} so'm\n"
    await msg.answer_video(video=video, caption=info, reply_markup=admin_group_save_buttons)
    await state.set_state(GroupStates.group_save)

@dp.callback_query(AdminFilter(), GroupStates.group_save)
async def group_save(call: CallbackQuery, state: FSMContext):
    if call.data == "save":
        await call.message.delete()
        data = await state.get_data()
        group_name = data.get("group_name")
        group_description = data.get("group_description")
        group_price = data.get("group_price")
        group_url = data.get("group_url")
        group_status = data.get("group_status")
        group_video = data.get("group_video")
        if data.get("product_id"):
            await db.update_product(data.get("product_id"), group_name, group_description,
                                    group_price, group_url, group_status, group_video)
        else:
            await db.add_product(group_name, group_description, group_price, group_url, group_status, group_video)
        await call.message.answer("✅ Guruh muvaffaqiyatli tarzda saqlandi.", reply_markup=admin_group_buttons)
        await state.clear()

    elif call.data == "edit":
        await call.message.delete()
        await call.message.answer("Guruh nomini kiriting: ")
        await state.set_state(GroupStates.group_name)
    elif call.data == "not save":
        await call.message.delete()
        await call.message.answer("Guruh rad etildi.", reply_markup=admin_group_buttons)
        await state.clear()


@dp.message(AdminFilter(), lambda msg: msg.text == "🔙 Ortga")
async def admin_panel(msg: types.Message):
    await msg.answer("Bosh panel.", reply_markup=admin_button)


# Show Groups panel --------------------------------------------------------------------------------------

@dp.message(lambda msg: msg.text == "📋 Guruhlar ro'yxati")
async def send_groups_list(msg: types.Message, state: FSMContext):
    await msg.answer("Qaysi guruhni ma'lumotini kormohchisiz?", reply_markup=await get_product_list())
    await state.set_state("get_group_id")


@dp.callback_query(AdminFilter(), StateFilter("get_group_id"), lambda call: call.data == "back")
async def admin_panel(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer("Guruhlar bo'limi.", reply_markup=admin_group_buttons)
    await state.clear()


@dp.callback_query(AdminFilter(), StateFilter("get_group_id"))
async def send_group_info(call: CallbackQuery, state: FSMContext):
    group_id = call.data
    data = await db.get_product(group_id)
    await call.message.delete()
    await state.update_data({"product_id": data[0]})
    video = data[-1]
    info = "📋 <b>Guruh haqida ma'lumot:</b>\n"
    info += f"👥 <b>Guruhning nomi:</b> {data[1]}\n"
    info += f"📝 <b>Guruhning ma'lumoti:</b> {data[2]}\n"
    info += f"🔗 <b>Guruhning ssilkasi:</b> {data[3]}\n"
    info += f"⚙️ <b>Guruhning xolati:</b>  {'✅' if data[5] == 'active' else '❌'}\n"
    info += f"💰 <b>Guruhning narxi:</b> {data[4]} so'm\n"
    await call.message.answer_video(video=video, caption=info, reply_markup=group_settings_button)
    await state.set_state("group_info")


@dp.callback_query(AdminFilter(), StateFilter("group_info"))
async def update_group(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    data = await state.get_data()
    if call.data == "edit":
        await add_group(call, state, pr_id=data.get("product_id"))
    elif call.data == "delete":
        await db.delete_product(data.get("product_id"))
        await call.message.answer("Guruh muvaffaqiyatli tarzda ochirildi.", reply_markup=admin_group_buttons)
        await state.clear()
    elif call.data == "back":
        await call.message.answer("Qaysi guruhni ma'lumotini kormohchisiz?", reply_markup=await get_product_list())
        await state.set_state("get_group_id")

