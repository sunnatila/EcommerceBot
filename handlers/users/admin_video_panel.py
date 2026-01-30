from aiogram.enums import ContentType
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from handlers.users.start import AdminFilter
from keyboards.default import admin_video_buttons, admin_button
from keyboards.inline import admin_settings_button
from loader import dp, db


@dp.message(AdminFilter(), lambda msg: msg.text == "🎞 Videolar bo'limi")
async def admin_video_panel(msg: Message, state: FSMContext):
    await msg.answer("Videolar bo'limida kerakli tugmachani bo'sing.", reply_markup=admin_video_buttons)


@dp.message(AdminFilter(), lambda msg: msg.text == "🔙 Ortga")
async def admin_video_back(msg: Message):
    await msg.answer("Iltimos, kerakli kategoriyani tanlang 😊", reply_markup=admin_button)


@dp.message(AdminFilter(), lambda msg: msg.text == "🎞 Video qo'shish")
async def admin_video_add(msg: Message, state: FSMContext):
    video = await db.get_videos()
    if video:
        await msg.answer("Video allaqachon yaratilgan. Oldin ochiring yoki tahrirlang.")
        return
    await msg.answer("Videoni tashlang.")
    await state.set_state("video_send")


@dp.message(AdminFilter(), StateFilter("video_send"), lambda msg: msg.content_type == ContentType.VIDEO)
async def admin_video_get_panel(msg: Message, state: FSMContext):
    video_url = msg.video.file_id
    await state.update_data({"video_url": video_url})
    await msg.answer("Video haqida ma'lumot kiriting:")
    await state.set_state("get_text_for_video")


@dp.message(AdminFilter(), StateFilter("get_text_for_video"))
async def get_video_text(msg: Message, state: FSMContext):
    desc = msg.text
    data = await state.get_data()
    video_id = data.get("video_id")
    if video_id:
        await db.update_video_info(video_id, data['video_url'], desc)
    else:
        await db.add_video(data["video_url"], desc)
    await msg.answer("Video muvaffaqiyatli tarzda qo'shildi yoki o'zgartirildi.", reply_markup=admin_button)
    await state.clear()



@dp.message(AdminFilter(), lambda msg: msg.text == "🎞 Videolar ro'yxati")
async def video_list_panel(msg: Message, state: FSMContext):
    videos = await db.get_videos()
    if videos:
        await state.update_data({"video_id": videos[0][0]})
        video_url = videos[0][1]
        video_desc = videos[0][2]
        await msg.answer_video(
            video=video_url,
            caption=video_desc,
            parse_mode="HTML",
            reply_markup=admin_settings_button
        )
        await state.set_state("video_data")
    else:
        await msg.answer("Videolar mavjud emas.", reply_markup=admin_button)
        await state.clear()



@dp.callback_query(AdminFilter(), StateFilter("video_data"))
async def video_data_panel(call: CallbackQuery, state: FSMContext):
    text = call.data
    data = await state.get_data()
    video_id = data["video_id"]
    if text == 'edit':
        await call.message.delete()
        await call.message.answer("Videoni tashlang.")
        await state.set_state("video_send")

    elif text == 'delete':
        await call.message.delete()
        await db.delete_video(video_id)
        await call.message.answer("Video muvaffaqiyatli ravishda ochib ketdi.", reply_markup=admin_button)
        await state.clear()

    else:
        await call.message.delete()
        await call.message.answer("Iltimos, kerakli kategoriyani tanlang 😊", reply_markup=admin_button)
        await state.clear()

