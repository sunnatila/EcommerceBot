from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from keyboards.default import user_buttons
from keyboards.inline import get_free_films, back_button
from loader import db, dp


@dp.message(lambda msg: msg.text == "🎥 Bonus filmlar")
async def send_bonus_films(msg: Message, state: FSMContext):
    await msg.answer("Ko'rmoqchi bo'lgan filmni tanlang:", reply_markup=await get_free_films())
    await state.set_state("get_free_film_id")


@dp.callback_query(StateFilter("get_free_film_id"), lambda call: call.data == "back")
async def back_func(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer("Bosh sahifa.", reply_markup=user_buttons)
    await state.clear()


@dp.callback_query(StateFilter("get_free_film_id"), lambda call: call.data.isdigit())
async def send_free_group_info(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    data = await db.get_product(call.data)
    video = data[-1]
    info = (
        f"👥 <b>Guruhning nomi:</b> {data[1]}\n\n"
        f"📝 <b>Guruhning ma'lumoti:</b> {data[2]}\n\n"
    )

    await call.message.answer_video(
        video=video,
        caption=info,
        parse_mode='HTML',
        reply_markup=await back_button(data[3])
    )
    await state.set_state("free_group_info")


@dp.callback_query(StateFilter("free_group_info"), lambda call: call.data == 'back')
async def back_to_free_films_list(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer("Ko'rmoqchi bo'lgan filmingizni tanlang:", reply_markup=await get_free_films())
    await state.set_state("get_free_film_id")
