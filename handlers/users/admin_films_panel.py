import re
from typing import Union

from aiogram import types
from aiogram.enums import ContentType
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove, CallbackQuery

from keyboards.inline import film_active_button, admin_film_save_buttons, get_product_list, film_settings_button, \
    product_paid_button
from .start import AdminFilter
from keyboards.default import admin_film_buttons, admin_button
from loader import db, bot, dp
from states import GroupStates


LINK_REGEX = r"https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)|https?://t\.me/[\w\+\-]+"


@dp.message(AdminFilter(), lambda msg: msg.text == "📋 Filmlar bo'limi")
async def film_panel(msg: types.Message):
    await msg.answer("Filmlar bo'limida kerak bo'lgan tugmachani bo'sing.", reply_markup=admin_film_buttons)


@dp.message(AdminFilter(), lambda msg: msg.text == "🔙 Ortga")
async def admin_panel(msg: types.Message, state: FSMContext):
    await msg.answer("Iltimos, kerakli kategoriyani tanlang 😊", reply_markup=admin_button)
    await state.clear()



# Create Group panel --------------------------------------------------------------------------------------



@dp.message(AdminFilter(), lambda msg: msg.text == "📋 Film qo'shish")
async def add_group(msg: Union[types.Message, CallbackQuery], state: FSMContext, pr_id=None):
    if isinstance(msg, CallbackQuery):
        await msg.message.answer("Film nomini kiriting:")
        await state.update_data({"product_id": pr_id})
    else:
        await msg.answer("Film nomini kiriting:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(GroupStates.film_name)


@dp.message(AdminFilter(), StateFilter(GroupStates.film_name), lambda msg: msg.content_type in [ContentType.TEXT])
async def get_film_name(msg: types.Message, state: FSMContext):
    await state.update_data({"film_name": msg.text})
    await msg.answer("Film haqida ma'lumot kiriting:")
    await state.set_state(GroupStates.film_description)


@dp.message(AdminFilter(), StateFilter(GroupStates.film_description), lambda msg: msg.content_type in [ContentType.TEXT])
async def get_film_description(msg: types.Message, state: FSMContext):
    await state.update_data({"film_description": msg.text})
    await msg.answer("Film bonusmi yoki pullik?", reply_markup=product_paid_button)
    await state.set_state(GroupStates.film_paid)

@dp.callback_query(AdminFilter(), StateFilter(GroupStates.film_paid))
async def get_film_paid(call: CallbackQuery, state: FSMContext):
    data = call.data
    await call.message.delete()
    if data == "free":
        await state.update_data({"film_price": 0})
        await call.message.answer("Film linkini kiriting:")
        await state.set_state(GroupStates.film_url)
    elif data == "paid":
        await call.message.answer("Film narxini kiriting (so'mda): ")
        await state.set_state(GroupStates.film_price)


@dp.message(AdminFilter(), StateFilter(GroupStates.film_price))
async def get_film_price(msg: types.Message, state: FSMContext):
    price = msg.text
    if price.isdigit():
        await state.update_data({"film_price": int(price)})
        await msg.answer("Film linkini kiriting:")
        await state.set_state(GroupStates.film_url)
        return
    await msg.answer("Film narxini faqat raqamlarda kiring!!\n"
                     "Misol uchun: 25000")


@dp.message(AdminFilter(), StateFilter(GroupStates.film_url), lambda msg: msg.content_type in [ContentType.TEXT])
async def get_film_url(msg: types.Message, state: FSMContext):
    url = msg.text.strip()
    if not re.match(LINK_REGEX, url):
        await msg.answer("Iltimos, to'g'ri link kiriting! Masalan: https://example.com yoki https://t.me/yourgroup")
        return
    await state.update_data({"film_url": url})
    await msg.answer("Film aktivmi?", reply_markup=film_active_button)
    await state.set_state(GroupStates.film_status)


@dp.callback_query(AdminFilter(), StateFilter(GroupStates.film_status))
async def get_film_status(call: CallbackQuery, state: FSMContext):
    await state.update_data({"film_status": call.data})
    await call.message.delete()
    await call.message.answer("Film haqida video tashlang:")
    await state.set_state(GroupStates.film_video)


@dp.message(AdminFilter(), StateFilter(GroupStates.film_video), lambda msg: msg.content_type in [ContentType.VIDEO])
async def get_film_image(msg: types.Message, state: FSMContext):
    video = msg.video.file_id
    await state.update_data({"film_video": video})
    await msg.delete()
    data = await state.get_data()
    info = "📋 <b>Film haqida ma'lumot:</b>\n"
    info += f"👥 <b>Filmning nomi:</b> {data.get('film_name')}\n"
    info += f"📝 <b>Filmning ma'lumoti:</b> {data.get('film_description')}\n"
    info += f"🔗 <b>Filmning ssilkasi:</b> {data.get('film_url')}\n"
    info += f"⚙️ <b>Filmning xolati:</b>  {'✅' if data.get('film_status') == 'active' else '❌'}\n"
    info += f"💰 <b>Filmning narxi:</b> {data.get('film_price')} so'm\n"
    await msg.answer_video(video=video, caption=info, reply_markup=admin_film_save_buttons)
    await state.set_state(GroupStates.film_save)


@dp.callback_query(AdminFilter(), StateFilter(GroupStates.film_save))
async def film_save(call: CallbackQuery, state: FSMContext):
    if call.data == "save":
        await call.message.delete()
        data = await state.get_data()
        film_name = data.get("film_name")
        film_description = data.get("film_description")
        film_price = data.get("film_price")
        film_url = data.get("film_url")
        film_status = data.get("film_status")
        film_video = data.get("film_video")
        if data.get("product_id"):
            await db.update_product(data.get("product_id"), film_name, film_description,
                                    film_price, film_url, film_status, film_video)
        else:
            await db.add_product(film_name, film_description, film_price, film_url, film_status, film_video)
        await call.message.answer("✅ Film muvaffaqiyatli tarzda saqlandi.", reply_markup=admin_film_buttons)
        await state.clear()

    elif call.data == "edit":
        await call.message.delete()
        await call.message.answer("Film nomini kiriting: ")
        await state.set_state(GroupStates.film_name)
    elif call.data == "not save":
        await call.message.delete()
        await call.message.answer("Film saqlanmadi.", reply_markup=admin_film_buttons)
        await state.clear()




# Show Groups panel --------------------------------------------------------------------------------------

@dp.message(AdminFilter(), lambda msg: msg.text == "📋 Filmlar ro'yxati")
async def send_groups_list(msg: types.Message, state: FSMContext):
    await msg.answer("Qaysi filmni ma'lumotini kormohchisiz?", reply_markup=await get_product_list())
    await state.set_state("get_film_id")


@dp.callback_query(AdminFilter(), StateFilter("get_film_id"), lambda call: call.data == "back")
async def admin_panel(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer("Filmlar bo'limi.", reply_markup=admin_film_buttons)
    await state.clear()


@dp.callback_query(AdminFilter(), StateFilter("get_film_id"))
async def send_film_info(call: CallbackQuery, state: FSMContext):
    film_id = call.data
    data = await db.get_product(film_id)
    await call.message.delete()
    await state.update_data({"product_id": data[0]})
    video = data[-1]
    info = "📋 <b>Film haqida ma'lumot:</b>\n"
    info += f"👥 <b>Filmning nomi:</b> {data[1]}\n"
    info += f"📝 <b>Filmning ma'lumoti:</b> {data[2]}\n"
    info += f"🔗 <b>Filmning ssilkasi:</b> {data[3]}\n"
    info += f"⚙️ <b>Filmning xolati:</b>  {'✅' if data[5] == 'active' else '❌'}\n"
    info += f"💰 <b>Filmning narxi:</b> {data[4]} so'm\n"
    await call.message.answer_video(video=video, caption=info, reply_markup=film_settings_button)
    await state.set_state("film_info")


@dp.callback_query(AdminFilter(), StateFilter("film_info"))
async def update_group(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    data = await state.get_data()
    if call.data == "edit":
        await add_group(call, state, pr_id=data.get("product_id"))
    elif call.data == "delete":
        await db.delete_product(data.get("product_id"))
        await call.message.answer("Film muvaffaqiyatli tarzda o'chirildi.", reply_markup=admin_film_buttons)
        await state.clear()
    elif call.data == "back":
        await call.message.answer("Qaysi filmni ma'lumotini ko'rmoqchisiz?", reply_markup=await get_product_list())
        await state.set_state("get_film_id")

