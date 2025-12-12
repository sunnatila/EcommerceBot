from aiogram.filters import StateFilter

from keyboards.default import user_buttons
from keyboards.inline import user_orders, back_button
from loader import db, dp
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext


@dp.message(lambda msg: msg.text == "🛒 Mening mahsulotlarim")
async def send_user_products(msg: Message, state: FSMContext):
    user_id = (await db.get_user_by_tg_id(msg.from_user.id))[0]
    await msg.answer("Kormohchi bo'lgan mahsulotingizni tanlang: ", reply_markup=await user_orders(user_id))
    await state.set_state("get_order_id")


@dp.callback_query(StateFilter("get_order_id"), lambda call: call.data == 'back')
async def back_func(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer("Bosh sahifa.", reply_markup=user_buttons)
    await state.clear()


@dp.callback_query(StateFilter("get_order_id"), lambda call: call.data.isdigit())
async def send_order_info(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    data = await db.get_product(call.data)
    video = data[-1]
    info = (
        f"👥 <b>Guruhning nomi:</b> {data[1]}\n\n"
        f"📝 <b>Guruhning ma'lumoti:</b> {data[2]}\n\n"
        f"🔗 <b>Guruhga qo'shilish:</b> <a href='{data[3]}'>Havola</a>\n"
    )

    await call.message.answer_video(
        video=video,
        caption=info,
        parse_mode='HTML',
        reply_markup=back_button
    )
    await state.set_state("order_info")


@dp.callback_query(StateFilter("order_info"), lambda call: call.data == 'back')
async def back_to_orders_list_func(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    user_id = (await db.get_user_by_tg_id(call.from_user.id))[0]
    await call.message.answer("Kormohchi bo'lgan mahsulotingizni tanlang:", reply_markup=await user_orders(user_id))
    await state.set_state("get_order_id")


