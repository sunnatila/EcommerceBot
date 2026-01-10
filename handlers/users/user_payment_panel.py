

from aiogram.types import Message, CallbackQuery, PreCheckoutQuery, ContentType, LabeledPrice

from data.config import CLICK_API, PAYME_API
from keyboards.default import user_buttons, get_active_products, back_button
from keyboards.inline import user_product_buttons, user_payment_chooser_button, group_link_button
from loader import dp, db, bot
from aiogram.fsm.context import FSMContext

from states import ProductStates


@dp.message(lambda msg: msg.text == "🎬 Filmlar bo'limi")
async def send_products(msg: Message, state: FSMContext):
    await msg.answer("Filmlardan birini tanlang!", reply_markup=await get_active_products())
    await state.set_state(ProductStates.products_page)


@dp.message(lambda msg: msg.text == '🔙 Ortga')
async def back_func(msg: Message, state: FSMContext):
    await msg.answer("Kategoriyadan birini tanlang.", reply_markup=user_buttons)
    await state.clear()

@dp.message(ProductStates.products_page)
async def get_product_id(msg: Message, state: FSMContext):
    product_name = msg.text
    data = await db.get_product_by_name(product_name)
    if not data:
        return

    product_id = data[0]
    user_row = await db.get_user_by_tg_id(msg.from_user.id)
    user_id = user_row[0] if user_row else None

    if user_id and await db.get_user_order(user_id, product_id):
        await msg.answer(
            text="Kinoni ko'rish uchun guruhga qo'shilish tugmachasini bo'sing!",
            reply_markup=await group_link_button(data[3]),
            protect_content = True
        )

        return
    await state.clear()
    video = data[-1]
    info = f"{data[1]}\n\n"
    info += f"{data[2]}\n\n"
    info += f"💰 <b>Narxi:</b> {data[4]} so'm\n\n"
    info += f"👇🏻 Sotib olish uchun pastdagi tugmani bosing!"

    await msg.answer(f"{msg.text} filmi haqida ma'lumot!", reply_markup=back_button)
    await msg.answer_video(video=video, caption=info, reply_markup=await user_product_buttons(product_id), parse_mode='HTML')


@dp.callback_query(lambda call: call.data.startswith('product_buy'))
async def send_payment_method(call: CallbackQuery, state: FSMContext):
    product_id = int(call.data.split('_')[-1])
    await state.update_data(product_id=product_id)
    inline_id = call.inline_message_id
    await call.message.edit_reply_markup(inline_id, reply_markup=user_payment_chooser_button)


@dp.callback_query(lambda call: call.data == 'present_product')
async def send_payment_method(call: CallbackQuery, state: FSMContext):
    text = ("""😊<b>Yaqiningizga film sovg'a qilish fikri ajoyib! Albatta manfaatli bo'ladi.</b>

    9860 1666 5328 6269
    Oybek Xolmirzayev (Humo)
    
    4231 2000 0859 1967
    Oybek Kholmirzaev (Visa)
    
    Kartaga ulangan nomer: +998990922002
    (Hamkorbank)
    
    Yuqoridagi kartalardan biriga ko'rsatilgan pulni tashlab:
    
    - chek
    - tanlagan audiokitobingiz
    - sovg'a qilmoqchi bo'lgan insoningiz kontaktini
    
    @ibratlivaqt_admin ga yuboring.
    
    🎁<b>Birgalikda filmni sovg'a qilamiz!</b>""")
    await call.message.answer(text)


@dp.callback_query(lambda call: call.data in ["click", "payme"])
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
    await message.answer(
        "To'lov muvaffaqiyatli amalga oshirildi!\n"
        "Filmlaringizni 'Mening Filmlarim' bo'limida ko'rishingiz mumkin.", reply_markup=user_buttons
    )
    data = await state.get_data()
    user_id = (await db.get_user_by_tg_id(message.from_user.id))[0]
    pr_id = data.get('product_id')
    await db.add_order(user_id, pr_id, 'is_paid')
    await state.clear()

