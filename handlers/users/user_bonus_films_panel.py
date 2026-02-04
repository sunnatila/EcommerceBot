from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from keyboards.default import user_buttons, get_free_films
from keyboards.inline import group_link_button
from loader import db, dp


@dp.message(lambda msg: msg.text == "🎥 Bonus filmlar")
async def send_bonus_films(msg: Message, state: FSMContext):
    await msg.answer("🎥 Ko‘rmoqchi bo‘lgan bonus filmingizni tanlang:", reply_markup=await get_free_films())
    await state.set_state("get_free_film_id")


@dp.message(StateFilter("get_free_film_id"))
async def send_free_group_info(msg: Message, state: FSMContext):
    data = await db.get_product_by_name(msg.text)
    if not data:
        return
    video = data[6]
    info = (
        f"<b>{data[1]}</b>\n\n"
        f"{data[2]}\n\n"
        f"Marhamat guruhga qo'shilib. Filmni tomosha qiling ☺️"
    )

    await msg.answer_video(
        video=video,
        caption=info,
        parse_mode='HTML',
        reply_markup=await group_link_button(data[7]),
        protect_content=True,
    )
