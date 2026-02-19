from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.default import user_buttons, get_active_products, back_button
from keyboards.inline import (
    user_product_buttons, group_link_button,
    sent_payment_url, all_pr_buy_buttons,
    resolution_buttons, all_resolution_buttons,
    get_payment_buttons, get_all_payment_buttons
)
from loader import dp, db
from utils.texts import get_text_with_admin
from states import ProductStates


@dp.message(lambda msg: msg.text == "🎬 Filmlar bo'limi")
async def send_products(msg: Message, state: FSMContext):
    await state.clear()
    await msg.answer("Har bir film sizga alohida tajriba taqdim etadi.", reply_markup=await get_active_products())
    await state.set_state(ProductStates.products_page)


@dp.message(lambda msg: msg.text == '🔙 Ortga')
async def back_func(msg: Message, state: FSMContext):
    await msg.answer("Kerakli bo'limni tanlang 😊", reply_markup=user_buttons)
    await state.clear()


@dp.message(ProductStates.products_page)
async def get_product_id(msg: Message, state: FSMContext):
    product_name = msg.text

    # ==================== CHEGIRMA BILAN OLISH ====================
    if product_name == "🎁 Chegirma bilan olish":
        await msg.answer(
            "<b>Qaysi sifatda tomosha qilishni xohlaysiz?</b>\n\n"
            "🎬 1080p - Yuqori sifat.\n"
            "💎 Gadjetlar uchun\n\n"
            "✨ 4K - Maksimal aniqlik.\n"
            "💎 TV va Kompyuterlar uchun",
            reply_markup=all_resolution_buttons,
            parse_mode='HTML'
        )
        return

    # ==================== BITTA FILM TANLASH ====================
    data = await db.get_product_by_name(product_name)
    if not data:
        return

    await state.update_data(product_id=data[0])
    await msg.answer(
        f"📺 <b>Qaysi sifatda tomosha qilishni xohlaysiz?</b>\n\n"
        f"🎬 1080p - Yuqori sifat.\n💎 Gadjetlar uchun\n💸 Tomosha narxi: {format_price(data[9])} so'm\n\n"
        f"✨ 4K - Maksimal aniqlik.\n💎 TV va Kompyuterlar uchun\n💸 Tomosha narxi: {format_price(data[10])} so'm",
        reply_markup=await resolution_buttons(pr_id=data[0]),
        parse_mode='HTML'
    )


# ==================== BITTA FILM - RESOLUTION TANLASH ====================
@dp.callback_query(lambda call: call.data.startswith('res_'))
async def select_resolution_single(call: CallbackQuery, state: FSMContext):
    resolution = call.data.replace('res_', '').split('_')[0]
    await call.message.delete()

    data = await state.get_data()
    product_id = data.get('product_id')

    user_row = await db.get_user_by_tg_id(call.from_user.id)
    user_ids = [user[0] for user in user_row] if user_row else []

    product = await db.get_product(product_id)

    if resolution == "4k":
        price = float(product[10])
        group_url = product[8]
    else:
        price = float(product[9])
        group_url = product[7]


    existing_order = None
    for user_id in user_ids:
        existing_order = await db.get_user_order(user_id, product_id, resolution)
        if existing_order:
            break

    if existing_order:
        await call.message.answer(
            f"✅ Siz bu filmni {resolution.upper()} sifatda allaqachon sotib olgansiz!\n\n"
            "Kinoni ko'rish uchun quyidagi tugmani bosing. 👇",
            reply_markup=await group_link_button(group_url),
            protect_content=True,
            parse_mode='HTML'
        )
        await state.set_state(ProductStates.products_page)
        return


    video = product[6]
    info = f"<b>{product[1]}</b>\n\n"
    info += f"{product[2]}\n\n"
    info += f"📺 <b>Sifat:</b> {resolution.upper()}\n"
    info += f"💎 <b>Filmni tomosha qilish</b>: {format_price(price)} so'm\n\n"
    info += "Davom etish uchun quyidagi tugmalardan foydalaning. 👇"

    await call.message.answer(f"\"{product[1]}\" filmidan qisqa lavha", reply_markup=back_button)
    await call.message.answer_video(
        video=video,
        caption=info,
        reply_markup=await user_product_buttons(product_id, resolution, int(price)),
        parse_mode='HTML'
    )
    await call.answer()


# ==================== BITTA FILM - SOTIB OLISH (STATE'SIZ) ====================
# buy_{product_id}_{resolution}_{price}
@dp.callback_query(lambda call: call.data.startswith('buy_'))
async def send_payment_method(call: CallbackQuery):
    parts = call.data.split('_')
    product_id = int(parts[1])
    resolution = parts[2]
    price = int(parts[3])

    await call.message.edit_reply_markup(
        reply_markup=get_payment_buttons(product_id, resolution, price)
    )
    await call.answer()


@dp.callback_query(lambda call: call.data == 'present_product')
async def send_present_product(call: CallbackQuery):
    text = await get_text_with_admin("present_product", db)
    await call.message.answer(text)
    await call.answer()


# pay_{method}_{product_id}_{resolution}_{price}
@dp.callback_query(lambda call: call.data.startswith('pay_'))
async def product_buy_func(call: CallbackQuery):
    parts = call.data.split('_')
    method = parts[1]
    product_id = int(parts[2])
    resolution = parts[3]
    price = int(parts[4])

    if method == 'other':
        await call.message.delete()
        text = await get_text_with_admin("other_payment_info", db)
        await call.message.answer(text, parse_mode='HTML')
        await call.message.answer("Kerakli bo'limni tanlang 😊", reply_markup=user_buttons)
        return

    user_row = await db.get_user_by_tg_id(call.from_user.id)
    user_id = user_row[0][0]

    payment_data = {
        "user": user_id,
        "product": [product_id],
        "count": 1,
        "resolution": resolution,
        "payment_method": method,
        "cost": price,
    }

    payment_markup = await sent_payment_url(payment_data)
    await call.message.edit_reply_markup(reply_markup=payment_markup)
    await call.answer()


# ==================== HAMMA FILMLAR - RESOLUTION TANLASH ====================
@dp.callback_query(lambda call: call.data.startswith('all_res_'))
async def select_resolution_all(call: CallbackQuery, state: FSMContext):
    resolution = call.data.replace('all_res_', '')
    await call.message.delete()
    await state.set_state(ProductStates.products_page)

    user_row = await db.get_user_by_tg_id(call.from_user.id)
    user_ids = [user[0] for user in user_row] if user_row else []


    if user_ids:

        all_purchased_ids = set()
        for user_id in user_ids:
            purchased = await db.get_user_purchased_products(user_id, resolution)
            if purchased:
                all_purchased_ids.update(p[0] for p in purchased)


        all_products = await db.get_active_products()
        unpurchased = [p for p in all_products if p[0] not in all_purchased_ids]
    else:
        unpurchased = await db.get_active_products()

    if not unpurchased:
        await call.message.answer(
            f"✅ <b>Tabriklaymiz!</b>\n\n"
            f"Siz barcha filmlarni {resolution.upper()} sifatda allaqachon sotib olgansiz! 🎉\n\n"
            "Yangi filmlar qo'shilishi bilanoq sizga xabar beramiz.",
            reply_markup=user_buttons,
            parse_mode='HTML'
        )
        await state.clear()
        return


    total_price = 0
    info = f"<b>🎁 Barcha filmlar uchun maxsus taklif</b>\n\n"
    info += f"<b> Barcha filmlar - {resolution.upper()} sifatda</b>\n\n"
    info += "<b>Filmlar bo'limidagi barcha filmlarni 20% chegirma bilan tomosha qilish imkoniyati.</b>\n\n"

    products_ids = []
    for i, product in enumerate(unpurchased, 1):
        if resolution == "4k":
            price = float(product[10])
        else:
            price = float(product[9])
        total_price += price
        products_ids.append(product[0])
        info += f"{i}. <b>{product[1]}</b>\n"
        info += f"   <s>{format_price(price)}</s> → <b>{format_price(price * 0.8)} so'm</b>\n\n"

    discount_price = int(total_price * 0.8)
    info += f"<b>📦 Umumiy filmlar soni:</b> {len(unpurchased)} ta\n"
    info += f"<b>💰 Umumiy qiymat:</b> <s>{format_price(total_price)}</s> so'm\n"
    info += f"<b>💎 Chegirmadan keyingi narx:</b> <b>{format_price(discount_price)} so'm</b>\n\n"
    info += "Davom etish uchun quyidagi tugmadan foydalaning. 👇"

    products_str = ".".join(map(str, products_ids))
    await call.message.answer(
        info,
        reply_markup=await all_pr_buy_buttons(products_str, resolution, discount_price),
        parse_mode='HTML'
    )
    await call.answer()

# ==================== HAMMA FILMLAR - SOTIB OLISH ====================
# allbuy_{products_str}_{resolution}_{price}
@dp.callback_query(lambda call: call.data.startswith('allbuy_'))
async def send_all_payment_method(call: CallbackQuery):
    parts = call.data.split('_')
    products_str = parts[1]
    resolution = parts[2]
    price = int(parts[3])

    await call.message.edit_reply_markup(
        reply_markup=get_all_payment_buttons(products_str, resolution, price)
    )
    await call.answer()


# allpay_{method}_{products_str}_{resolution}_{price}
@dp.callback_query(lambda call: call.data.startswith('allpay_'))
async def all_product_buy_func(call: CallbackQuery):
    parts = call.data.split('_')
    method = parts[1]
    products_str = parts[2]
    resolution = parts[3]
    price = int(parts[4])

    products_ids = [int(x) for x in products_str.split('.')]
    user_row = await db.get_user_by_tg_id(call.from_user.id)
    user_data = user_row[0]

    if method == 'other':
        await call.message.delete()
        info = f"Hurmatli <b>{user_data[1]}</b>,\n\n"
        info += f"📺 <b>Sifat:</b> {resolution.upper()}\n\n"
        info += "Quyidagi filmlar uchun to'lov:\n\n"
        for i, product_id in enumerate(products_ids, 1):
            product = await db.get_product(product_id)
            info += f"<b>{i}. {product[1]}</b>\n"
        info += f"\n💰 <b>UMUMIY TO'LOV:</b> {format_price(price)} so'm\n\n"
        info += await get_text_with_admin("other_payment_info", db)
        await call.message.answer(info, parse_mode='HTML')
        await call.message.answer("Kerakli bo'limni tanlang 😊", reply_markup=user_buttons)
        return

    user_id = user_data[0]
    payment_data = {
        "user": user_id,
        "product": products_ids,
        "count": len(products_ids),
        "resolution": resolution,
        "payment_method": method,
        "cost": price,
    }

    payment_markup = await sent_payment_url(payment_data)
    await call.message.edit_reply_markup(reply_markup=payment_markup)
    await call.answer()

def format_price(price):
    if price is None:
        return "0"
    return f"{int(price):,}".replace(',', ' ')