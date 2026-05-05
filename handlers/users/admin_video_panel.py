from aiogram.enums import ContentType
from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from handlers.users.start import AdminFilter
from keyboards.default import admin_video_buttons, admin_button
from keyboards.inline import video_settings_button
from loader import dp, db, bot


@dp.message(AdminFilter(), lambda msg: msg.text == "🎞 Videolar bo'limi")
async def admin_video_panel(msg: Message, state: FSMContext):
    await msg.answer("Videolar bo'limida kerakli tugmachani bo'sing.", reply_markup=admin_video_buttons)


@dp.message(AdminFilter(), lambda msg: msg.text == "🔙 Ortga")
async def admin_video_back(msg: Message):
    await msg.answer("Iltimos, kerakli kategoriyani tanlang 😊", reply_markup=admin_button)



@dp.message(AdminFilter(), lambda msg: msg.text == "🎞 Video qo'shish")
async def admin_video_add(msg: Message, state: FSMContext):
    await msg.answer("Videoni tashlang.")
    await state.set_state("video_send")


@dp.message(AdminFilter(), StateFilter("video_send"), lambda msg: msg.content_type == ContentType.VIDEO)
async def admin_video_get_panel(msg: Message, state: FSMContext):
    video_url = msg.video.file_id
    await state.update_data({"video_url": video_url})
    await msg.answer("Video haqida ma'lumot kiriting:")
    await state.set_state("get_video_text")


@dp.message(AdminFilter(), StateFilter("get_video_text"))
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


@dp.message(AdminFilter(), lambda msg: msg.text == "🎥 Video yuborish")
async def admin_video_add(msg: Message, state: FSMContext):
    await msg.answer("Videoni tashlang.")
    await state.set_state("get_video_url")


@dp.message(AdminFilter(), StateFilter("get_video_url"), lambda msg: msg.content_type == ContentType.VIDEO)
async def admin_video_get(msg: Message, state: FSMContext):
    video_url = msg.video.file_id
    await state.update_data({"video_url": video_url})
    await msg.answer("Video haqida ma'lumot kiriting:")
    await state.set_state("get_text_for_video")


@dp.message(AdminFilter(), StateFilter("get_text_for_video"))
async def get_text_for_video(msg: Message, state: FSMContext):
    desc = msg.text
    data = await state.get_data()
    video_id = data.get("video_url")
    if video_id:
        users_data = await db.get_users()
        for user in users_data:
            try:
                await bot.send_video(chat_id=user[0], video=data['video_url'], caption=desc)
            except:
                pass
    await msg.answer("Video muvaffaqiyatli tarzda foydalanuvchilarga yuborildi.", reply_markup=admin_button)
    await state.clear()



@dp.message(AdminFilter(), lambda msg: msg.text == "🎞 Videolar ro'yxati")
async def video_list_panel(msg: Message, state: FSMContext):
    videos = await db.get_videos()
    if not videos:
        await msg.answer("Videolar mavjud emas.", reply_markup=admin_button)
        await state.clear()
        return

    for video in videos:
        video_id = video[0]
        video_url = video[1]
        video_desc = video[2]
        await msg.answer_video(
            video=video_url,
            caption=video_desc,
            parse_mode="HTML",
            reply_markup=video_settings_button(video_id)
        )


@dp.callback_query(AdminFilter(), lambda call: call.data and call.data.startswith(("video_edit:", "video_delete:")))
async def video_data_panel(call: CallbackQuery, state: FSMContext):
    action, video_id = call.data.split(":", 1)
    video_id = int(video_id)

    if action == "video_edit":
        await state.update_data({"video_id": video_id})
        await call.message.delete()
        await call.message.answer("Videoni tashlang.")
        await state.set_state("video_send")

    elif action == "video_delete":
        await call.message.delete()
        await db.delete_video(video_id)
        await call.message.answer("Video muvaffaqiyatli ravishda o'chirib tashlandi.", reply_markup=admin_button)
        await state.clear()
