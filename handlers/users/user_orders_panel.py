from aiogram.filters import StateFilter

from keyboards.default import user_buttons, user_orders
from keyboards.inline import group_link_button
from loader import db, dp
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext


@dp.message(lambda msg: msg.text == "🎞 Mening Filmlarim")
async def send_user_products(msg: Message, state: FSMContext):
    user_id = (await db.get_user_by_tg_id(msg.from_user.id))[0]
    await msg.answer("Sizning film kolleksiyangiz:", reply_markup=await user_orders(user_id))
    await state.set_state("get_order_id")


@dp.callback_query(lambda call: call.data == 'back')
async def back_func(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer("Kerakli bo'limni tanlang 😊", reply_markup=user_buttons)
    await state.clear()


@dp.message(StateFilter("get_order_id"))
async def send_order_info(msg: Message, state: FSMContext):
    product_name = msg.text
    data = await db.get_product_by_name(product_name)
    if not data:
        return
    await msg.answer(
        text="Kinoni ko‘rish uchun guruhga qo‘shilish tugmasini bosing 👇",
        reply_markup=await group_link_button(data[3]),
        protect_content = True
    )
    await state.clear()
