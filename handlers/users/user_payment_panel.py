from aiogram.types import Message, CallbackQuery
from keyboards.default import user_buttons, get_active_products, back_button
from keyboards.inline import user_product_buttons, user_payment_chooser_button, group_link_button, sent_payment_url, \
    all_pr_buy_buttons, all_product_payment_chooser_button
from loader import dp, db, bot
from aiogram.fsm.context import FSMContext
from utils.texts import get_text
from states import ProductStates


@dp.message(lambda msg: msg.text == "🎬 Filmlar bo'limi")
async def send_products(msg: Message, state: FSMContext):
    await msg.answer("Har bir film sizga alohida tajriba taqdim etadi.", reply_markup=await get_active_products())
    await state.set_state(ProductStates.products_page)


@dp.message(lambda msg: msg.text == '🔙 Ortga')
async def back_func(msg: Message, state: FSMContext):
    await msg.answer("Kerakli bo'limni tanlang 😊", reply_markup=user_buttons)
    await state.clear()

@dp.message(ProductStates.products_page)
async def get_product_id(msg: Message, state: FSMContext):
    product_name = msg.text

    if product_name == "🎁 Chegirma bilan olish":
        info = "<b>🎁 Barcha filmlar uchun maxsus taklif</b>\n\n"
        info += "<b>Filmlar bo‘limidagi barcha filmlarni 20% chegirma bilan tomosha qilish imkoniyati.</b>\n\n"
        all_products = await db.get_active_products()
        if all_products:
            total_price = 0
            index = 1
            for product in all_products:
                price = float(product[4])
                total_price += price
                info += f"{index}. {product[1]}\n"
                info += f"<s>{int(price)}</s> → {int(price * 0.8)} so'm\n\n"
                index += 1
            discount_price = total_price * 0.8
            await state.update_data(
                price=discount_price,
                products_id=[product[0] for product in all_products],
            )
            info += f"<b>📦 Umumiy filmlar soni:</b> <b>{len(all_products)}</b> ta\n"
            info += f"<b>💰 Umumiy qiymat:</b> <s>{int(total_price)}</s> so'm\n"
            info += f"<b>💎 Chegirmadan keyingi narx:</b> {int(discount_price)} so'm\n\n"
            info += "Davom etish uchun quyidagi tugmadan foydalaning."
            await msg.answer(info, reply_markup=await all_pr_buy_buttons(), parse_mode='HTML')
        else:
            await msg.answer("Hozircha sotuvda hech qanday film mavjud emas 😊", reply_markup=user_buttons)
        await state.set_state(ProductStates.products_page)
        return
    await state.clear()
    data = await db.get_product_by_name(product_name)
    if not data:
        return

    product_id = data[0]
    user_row = await db.get_user_by_tg_id(msg.from_user.id)
    user_id = user_row[0] if user_row else None

    if user_id and await db.get_user_order(user_id, product_id):
        await msg.answer(
            text="Kinoni ko'rish uchun guruhga qo'shilish tugmasini bosing 👇",
            reply_markup=await group_link_button(data[3]),
            protect_content = True
        )
        return
    video = data[-1]
    info = f"<b>{data[1]}</b>\n\n"
    info += f"{data[2]}\n\n"
    info += f"<b>💎 Filmni tomosha qilish:</b> {int(data[4])} so'm\n\n"
    info += "Davom etish uchun quyidagi tugmalardan foydalaning."

    await msg.answer(f"\"{msg.text}\" filmidan qisqa lavha", reply_markup=back_button)
    await msg.answer_video(video=video, caption=info, reply_markup=await user_product_buttons(product_id), parse_mode='HTML')


@dp.callback_query(lambda call: call.data.startswith('product_buy'))
async def send_payment_method(call: CallbackQuery, state: FSMContext):
    product_id = int(call.data.split('_')[-1])
    await state.update_data(product_id=product_id)
    await call.message.edit_reply_markup(reply_markup=user_payment_chooser_button)
    await call.answer()


@dp.callback_query(lambda call: call.data.startswith('all_product_buy'))
async def send_payment_method(call: CallbackQuery, state: FSMContext):
    await call.message.edit_reply_markup(reply_markup=all_product_payment_chooser_button)
    await call.answer()


@dp.callback_query(lambda call: call.data == 'present_product')
async def send_present_product(call: CallbackQuery, state: FSMContext):
    text = get_text("present_product")
    await call.message.answer(text)
    await call.answer()


@dp.callback_query(lambda call: call.data in ["click", "payme", "other_payment"])
async def product_buy_func(call: CallbackQuery, state: FSMContext):
    if call.data == 'other_payment':
        await call.message.delete()
        text = get_text("other_payment_info")
        await call.message.answer(text)
        await call.answer()
        return
    data = await state.get_data()
    user_id = (await db.get_user_by_tg_id(call.from_user.id))[0]
    product_id = data.get("product_id")
    product_data = await db.get_product(product_id)
    price = float(product_data[4])
    payment_method = call.data
    count = 1
    data = {
        "user": user_id,
        "product": [product_id],
        "count": count,
        "payment_method": payment_method,
        "cost": price,
    }
    payment_markup = await sent_payment_url(data)
    await call.message.edit_reply_markup(reply_markup=payment_markup)
    await call.answer()



@dp.callback_query(lambda call: call.data in ["all_product_click", "all_product_payme", "all_product_other_payment"])
async def all_product_buy_func(call: CallbackQuery, state: FSMContext):
    user_data = await db.get_user_by_tg_id(call.from_user.id)
    payment_method = call.data.replace("all_product_", "")
    all_products = await db.get_active_products()
    product_data = await state.get_data()
    if payment_method == 'other_payment':
        await call.message.delete()
        index = 1
        info = f"Hurmatli {user_data[1]},\n\n"
        info += "sizga quyidagi filmlarni taqdim etishimiz uchun quyidagi to'lovni amalga oshirishingiz kerak:\n\n"
        for product in all_products:
            info += f"<b>{index}. {product[1]}</b>\n"
            index += 1

        discount_price = product_data.get("price")
        info += f"\n💰 UMUMIY TO'LOV: <b>{int(discount_price)}</b> so'm.\n\n"
        info += get_text("other_payment_info")
        await call.message.answer(info, parse_mode='HTML')
        await call.message.answer("Kerakli bo'limni tanlang 😊", reply_markup=user_buttons)
        await call.answer()
        return
    user_id = user_data[0]
    products_id = product_data.get("products_id")
    price = float(product_data.get("price"))
    data = {
        "user": user_id,
        "product": products_id,
        "count": len(products_id),
        "payment_method": payment_method,
        "cost": price,
    }
    payment_markup = await sent_payment_url(data)
    await call.message.edit_reply_markup(reply_markup=payment_markup)
    await call.answer()

