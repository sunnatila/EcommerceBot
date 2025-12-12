

from aiogram.types import Message, CallbackQuery, PreCheckoutQuery, ContentType, LabeledPrice

from data.config import CLICK_API, PAYME_API
from keyboards.default import user_buttons
from keyboards.inline import get_active_products, user_product_buttons, user_payment_chooser_button
from loader import dp, db, bot
from aiogram.fsm.context import FSMContext

from states import ProductStates


@dp.message(lambda msg: msg.text == "📦 Mahsulotlar bo'limi")
async def send_products(msg: Message, state: FSMContext):
    await msg.answer("Sotib olmohchi bo'lgan mahsulotni tanlang:", reply_markup=await get_active_products())
    await state.set_state(ProductStates.products_page)

@dp.callback_query(ProductStates.products_page, lambda call: call.data == 'back')
async def back_func(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    await call.message.answer("Bosh sahifa.", reply_markup=user_buttons)
    await state.clear()


@dp.callback_query(ProductStates.products_page, lambda call: call.data.isdigit())
async def get_product_id(call: CallbackQuery, state: FSMContext):
    product_id = call.data
    await call.message.delete()
    await state.update_data({"product_id": product_id})
    user_id = (await db.get_user_by_tg_id(call.from_user.id))[0]
    if await db.get_user_order(user_id, product_id):
        await call.message.answer("Siz bu mahsulotni allaqachon sotib olgansiz!", reply_markup=user_buttons)
        await state.clear()
        return
    data = await db.get_product(product_id)
    video = data[-1]
    info = f"👥 <b>Guruhning nomi:</b> {data[1]}\n\n"
    info += f"📝 <b>Guruhning ma'lumoti:</b> {data[2]}\n\n"
    info += f"💰 <b>Guruhning narxi:</b> {data[4]} so'm\n"
    await call.message.answer_video(video=video, caption=info, reply_markup=user_product_buttons)
    await state.set_state(ProductStates.product_info)


@dp.callback_query(ProductStates.product_info, lambda call: call.data == 'product_buy')
async def send_payment_method(call: CallbackQuery, state: FSMContext):
    inline_id = call.inline_message_id
    await call.message.edit_reply_markup(inline_id, reply_markup=user_payment_chooser_button)
    await state.set_state(ProductStates.product_payment)

@dp.callback_query(ProductStates.product_payment)
async def product_buy_func(call: CallbackQuery, state: FSMContext):
    await call.message.delete()
    data = await state.get_data()
    product_id = data.get("product_id")
    product_data = await db.get_product(product_id)
    start_parameter = f"buy_product_{product_id}"
    payload = f"order_{product_id}_{call.from_user.id}"
    prices = [LabeledPrice(label="Ummumiy summa", amount=product_data[4] * 100)]
    if call.data == "click":
        provider_token = CLICK_API
    else:
        provider_token = PAYME_API

    await call.message.answer_invoice(
        title=product_data[1],
        description=product_data[2],
        payload=payload,
        provider_token=provider_token,
        currency="uzs",
        prices=prices,
        start_parameter=start_parameter,
        need_email=True,
        need_phone_number=True
    )


@dp.pre_checkout_query()
async def pre_checkout_query(pre_checkout_q: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)

@dp.message(lambda msg: msg.content_type in [ContentType.SUCCESSFUL_PAYMENT])
async def successful_payment(message: Message, state: FSMContext):
    await message.answer("To'lov muvaffaqiyatli amalga oshirildi!\n"
                         "Mahsulotlaringizni 'Mening mahsulotlarim' bo'limida korishingiz mumkin.", reply_markup=user_buttons)

    data = await state.get_data()
    user_id = (await db.get_user_by_tg_id(message.from_user.id))[0]
    pr_id = data.get('product_id')
    await db.add_order(user_id, pr_id, 'is_paid')
    await state.clear()

