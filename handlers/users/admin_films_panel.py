import re
from typing import Union

from aiogram import types
from aiogram.enums import ContentType
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove, CallbackQuery

from keyboards.inline import (film_active_button, admin_film_save_buttons, get_product_list,
                              film_settings_button, product_paid_button)
from .start import AdminFilter
from keyboards.default import admin_film_buttons, admin_button
from loader import db, dp
from states import GroupStates

LINK_REGEX = r"https?://(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&//=]*)|https?://t\.me/[\w\+\-]+"


@dp.message(AdminFilter(), lambda msg: msg.text == "🎞 Filmlar bo'limi")
async def film_panel(msg: types.Message):
    await msg.answer("Filmlar bo'limida kerak bo'lgan tugmachani bosing.", reply_markup=admin_film_buttons)


@dp.message(AdminFilter(), lambda msg: msg.text == "🔙 Ortga")
async def admin_panel(msg: types.Message, state: FSMContext):
    await msg.answer("Iltimos, kerakli kategoriyani tanlang 😊", reply_markup=admin_button)
    await state.clear()


# ==================== FILM QO'SHISH ====================

@dp.message(AdminFilter(), lambda msg: msg.text == "🎞 Film qo'shish")
async def add_group(msg: Union[types.Message, CallbackQuery], state: FSMContext, pr_id=None):
    if isinstance(msg, CallbackQuery):
        await msg.message.answer("Film nomini kiriting:")
        await state.update_data(product_id=pr_id)
    else:
        await msg.answer("Film nomini kiriting:", reply_markup=ReplyKeyboardRemove())
    await state.set_state(GroupStates.film_name)


@dp.message(AdminFilter(), StateFilter(GroupStates.film_name), lambda msg: msg.content_type == ContentType.TEXT)
async def get_film_name(msg: types.Message, state: FSMContext):
    await state.update_data(film_name=msg.text)
    await msg.answer("Film haqida ma'lumot kiriting:")
    await state.set_state(GroupStates.film_description)


@dp.message(AdminFilter(), StateFilter(GroupStates.film_description), lambda msg: msg.content_type == ContentType.TEXT)
async def get_film_description(msg: types.Message, state: FSMContext):
    await state.update_data(film_description=msg.text)
    await msg.answer("Film bonusmi yoki pullik?", reply_markup=product_paid_button)
    await state.set_state(GroupStates.film_paid)


@dp.callback_query(AdminFilter(), StateFilter(GroupStates.film_paid))
async def get_film_paid(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    if call.data == "free":
        await state.update_data(
            film_price_1080p=0,
            film_price_4k=0,
            film_url_1080p="",
            film_url_4k=""
        )
        await call.message.answer("Bonus film uchun guruh linkini kiriting:")
        await state.set_state(GroupStates.film_url_1080p)
    else:
        await call.message.answer("📺 1080p narxini kiriting (so'mda):")
        await state.set_state(GroupStates.film_price_1080p)


# 1080p narxi
@dp.message(AdminFilter(), StateFilter(GroupStates.film_price_1080p))
async def get_film_price_1080p(msg: types.Message, state: FSMContext):
    if not msg.text.isdigit():
        await msg.answer("Faqat raqam kiriting! Misol: 25000")
        return
    await state.update_data(film_price_1080p=int(msg.text))
    await msg.answer("📺 1080p guruh linkini kiriting:")
    await state.set_state(GroupStates.film_url_1080p)


# 1080p link
@dp.message(AdminFilter(), StateFilter(GroupStates.film_url_1080p), lambda msg: msg.content_type == ContentType.TEXT)
async def get_film_url_1080p(msg: types.Message, state: FSMContext):
    url = msg.text.strip()
    data = await state.get_data()

    # Agar bonus film bo'lsa, faqat bitta link
    if data.get('film_price_1080p') == 0 and data.get('film_price_4k') == 0:
        if url and not re.match(LINK_REGEX, url):
            await msg.answer("Iltimos, to'g'ri link kiriting!")
            return
        await state.update_data(film_url_1080p=url, film_url_4k=url)
        await msg.answer("Film aktivmi?", reply_markup=film_active_button)
        await state.set_state(GroupStates.film_status)
        return

    if not re.match(LINK_REGEX, url):
        await msg.answer("Iltimos, to'g'ri link kiriting! Masalan: https://t.me/yourgroup")
        return
    await state.update_data(film_url_1080p=url)
    await msg.answer("📺 4K narxini kiriting (so'mda):")
    await state.set_state(GroupStates.film_price_4k)


# 4K narxi
@dp.message(AdminFilter(), StateFilter(GroupStates.film_price_4k))
async def get_film_price_4k(msg: types.Message, state: FSMContext):
    if not msg.text.isdigit():
        await msg.answer("Faqat raqam kiriting! Misol: 35000")
        return
    await state.update_data(film_price_4k=int(msg.text))
    await msg.answer("📺 4K guruh linkini kiriting:")
    await state.set_state(GroupStates.film_url_4k)


# 4K link
@dp.message(AdminFilter(), StateFilter(GroupStates.film_url_4k), lambda msg: msg.content_type == ContentType.TEXT)
async def get_film_url_4k(msg: types.Message, state: FSMContext):
    url = msg.text.strip()
    if not re.match(LINK_REGEX, url):
        await msg.answer("Iltimos, to'g'ri link kiriting! Masalan: https://t.me/yourgroup")
        return
    await state.update_data(film_url_4k=url)
    await msg.answer("Film aktivmi?", reply_markup=film_active_button)
    await state.set_state(GroupStates.film_status)


@dp.callback_query(AdminFilter(), StateFilter(GroupStates.film_status))
async def get_film_status(call: CallbackQuery, state: FSMContext):
    await state.update_data(film_status=call.data)
    await call.message.delete()
    await call.message.answer("Film haqida video tashlang:")
    await state.set_state(GroupStates.film_video)


@dp.message(AdminFilter(), StateFilter(GroupStates.film_video), lambda msg: msg.content_type == ContentType.VIDEO)
async def get_film_video(msg: types.Message, state: FSMContext):
    video = msg.video.file_id
    await state.update_data(film_video=video)
    await msg.delete()

    data = await state.get_data()
    info = "📋 <b>Film haqida ma'lumot:</b>\n\n"
    info += f"🎬 <b>Nomi:</b> {data.get('film_name')}\n"
    info += f"📝 <b>Ma'lumot:</b> {data.get('film_description')}\n\n"
    info += f"📺 <b>1080p narxi:</b> {format_price(data.get('film_price_1080p'))} so'm\n"
    info += f"🔗 <b>1080p link:</b> {data.get('film_url_1080p') or 'Yo`q'}\n\n"
    info += f"📺 <b>4K narxi:</b> {format_price(data.get('film_price_4k'))} so'm\n"
    info += f"🔗 <b>4K link:</b> {data.get('film_url_4k') or 'Yo`q'}\n\n"
    info += f"⚙️ <b>Holati:</b> {'✅ Aktiv' if data.get('film_status') == 'active' else '❌ Aktiv emas'}\n"

    await msg.answer_video(video=video, caption=info, reply_markup=admin_film_save_buttons)
    await state.set_state(GroupStates.film_save)


@dp.callback_query(AdminFilter(), StateFilter(GroupStates.film_save))
async def film_save(call: CallbackQuery, state: FSMContext):
    await call.message.delete()

    if call.data == "save":
        data = await state.get_data()

        if data.get("product_id"):
            await db.update_product(
                data.get("product_id"),
                data.get("film_name"),
                data.get("film_description"),
                data.get("film_price_1080p"),
                data.get("film_url_1080p"),
                data.get("film_price_4k"),
                data.get("film_url_4k"),
                data.get("film_status"),
                data.get("film_video")
            )
        else:
            await db.add_product(
                data.get("film_name"),
                data.get("film_description"),
                data.get("film_price_1080p"),
                data.get("film_url_1080p"),
                data.get("film_price_4k"),
                data.get("film_url_4k"),
                data.get("film_status"),
                data.get("film_video")
            )

        await call.message.answer("✅ Film muvaffaqiyatli saqlandi.", reply_markup=admin_film_buttons)
        await state.clear()

    elif call.data == "edit":
        await call.message.answer("Film nomini kiriting:")
        await state.set_state(GroupStates.film_name)

    elif call.data == "not save":
        await call.message.answer("Film saqlanmadi.", reply_markup=admin_film_buttons)
        await state.clear()


# ==================== FILMLAR RO'YXATI ====================

@dp.message(AdminFilter(), lambda msg: msg.text == "🎞 Filmlar ro'yxati")
async def send_groups_list(msg: types.Message, state: FSMContext):
    await msg.answer("Qaysi filmni ma'lumotini ko'rmoqchisiz?", reply_markup=await get_product_list())
    await state.set_state("get_film_id")


@dp.callback_query(AdminFilter(), StateFilter("get_film_id"), lambda call: call.data == "back")
async def admin_panel_back(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer("Filmlar bo'limi.", reply_markup=admin_film_buttons)
    await state.clear()


@dp.callback_query(AdminFilter(), StateFilter("get_film_id"))
async def send_film_info(call: CallbackQuery, state: FSMContext):
    film_id = call.data
    data = await db.get_product(film_id)
    await call.message.delete()
    await state.update_data(product_id=data[0])

    # data: id, title, description, is_active, created_at, updated_at, video_url, 1080p url, 4k url, 1080p price, 4k price
    video = data[6]  # video_url
    info = "📋 <b>Film haqida ma'lumot:</b>\n\n"
    info += f"🎬 <b>Nomi:</b> {data[1]}\n"
    info += f"📝 <b>Ma'lumot:</b> {data[2]}\n\n"
    info += f"📺 <b>1080p narxi:</b> {format_price(data[9])} so'm\n"
    info += f"🔗 <b>1080p link:</b> {data[7] or 'Yo`q'}\n\n"
    info += f"📺 <b>4K narxi:</b> {format_price(data[10])} so'm\n"
    info += f"🔗 <b>4K link:</b> {data[8] or 'Yo`q'}\n\n"
    info += f"⚙️ <b>Holati:</b> {'✅ Aktiv' if data[3] == 'active' else '❌ Aktiv emas'}\n"

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
        await call.message.answer("Film muvaffaqiyatli o'chirildi.", reply_markup=admin_film_buttons)
        await state.clear()
    elif call.data == "back":
        await call.message.answer("Qaysi filmni ma'lumotini ko'rmoqchisiz?", reply_markup=await get_product_list())
        await state.set_state("get_film_id")


def format_price(price):
    if price is None:
        return "0"
    return f"{int(price):,}".replace(',', ' ')