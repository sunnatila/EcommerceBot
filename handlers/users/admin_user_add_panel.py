from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.default import admin_button, get_users_panel_buttons, get_products_for_admin
from keyboards.inline import resolution_buttons
from .start import AdminFilter
from loader import db, dp


@dp.message(AdminFilter(), lambda msg: msg.text == "👤 Foydalanuvchilar bo'limi")
async def send_users_panel(msg: Message, state: FSMContext):
    await msg.answer("Foydalanuvchilar bo'limidan kerak bo'lgan tugmachani bosing:",
                     reply_markup=get_users_panel_buttons)


@dp.message(AdminFilter(), lambda msg: msg.text == '🔙 Ortga')
async def back_to_menu(msg: Message, state: FSMContext):
    await msg.answer("Iltimos, kerakli kategoriyani tanlang 😊", reply_markup=admin_button)
    await state.clear()


@dp.message(AdminFilter(), lambda msg: msg.text == "👤 Foydalanuvchiga film qo'shish")
async def add_user(msg: Message, state: FSMContext):
    await msg.answer("Foydalanuvchini kontaktini kiriting yoki tashlang:")
    await state.set_state("user_contact_get")


@dp.message(AdminFilter(), StateFilter("user_contact_get"))
async def user_contact_get(msg: Message, state: FSMContext):
    text = msg.contact.phone_number if msg.contact else msg.text

    if text.startswith('+998') and text[4:].isdigit() and len(text) == 13:
        pass
    elif text.isdigit() and len(text) == 9:
        text = '+998' + text
    else:
        await msg.answer(
            "❌ Telefon raqam noto'g'ri kiritildi.\n"
            "Iltimos, telefon raqamini qaytadan kiriting (namuna: +99890xxxxxxx yoki 90xxxxxxx)."
        )
        return

    await state.update_data(contact=text)
    await msg.answer("To'langan summani kiriting:")
    await state.set_state("get_paid_sum")


@dp.message(AdminFilter(), StateFilter("get_paid_sum"))
async def get_paid_sum(msg: Message, state: FSMContext):
    if not msg.text.isdigit():
        await msg.answer("Faqat raqam kiriting!")
        return

    await state.update_data(cost=float(msg.text))
    await msg.answer(
        "📺 Qaysi sifatda ruxsat bermoqchisiz?",
        reply_markup=resolution_buttons
    )
    await state.set_state("get_resolution")


@dp.callback_query(AdminFilter(), StateFilter("get_resolution"), lambda call: call.data.startswith('res_'))
async def get_resolution(call: CallbackQuery, state: FSMContext):
    resolution = call.data.replace('res_', '')
    await state.update_data(resolution=resolution)
    await call.message.delete()
    await call.message.answer(
        "Qaysi filmga ruxsat bermoqchisiz?",
        reply_markup=await get_products_for_admin()
    )
    await state.set_state("groups_get")


@dp.message(AdminFilter(), StateFilter("groups_get"))
async def groups_get(msg: Message, state: FSMContext):
    data = await state.get_data()
    contact = data.get("contact")
    cost = data.get("cost")
    resolution = data.get("resolution")
    text = msg.text

    user_info = await db.get_user_by_phone(contact)

    # ==================== BITTA FILM ====================
    if text != "Hamma filmlarga ruxsat berish":
        product = await db.get_product_by_name(text)
        if not product:
            await msg.answer("❌ Bunday film topilmadi.", parse_mode="HTML")
            return

        product_id = product[0]
        product_title = product[1]

        # Yangi foydalanuvchi
        if not user_info:
            await db.add_user_by_admin(contact, cost, [product_id], resolution)
            await msg.answer(
                f"✅ <b>Muvaffaqiyatli!</b>\n\n"
                f"📱 Telefon: <code>{contact}</code>\n"
                f"🎬 Film: <b>{product_title}</b>\n"
                f"📺 Sifat: <b>{resolution.upper()}</b>\n"
                f"💰 To'lov: <b>{format_price(cost)} so'm</b>",
                reply_markup=admin_button,
                parse_mode="HTML"
            )
            await state.clear()
            return

        # Mavjud foydalanuvchi
        user_id = user_info[0]
        existing = await db.get_user_order(user_id, product_id, resolution)

        if existing:
            await msg.answer(
                f"⚠️ Bu foydalanuvchiga {product_title} filmiga "
                f"{resolution.upper()} sifatda allaqachon ruxsat berilgan!",
                parse_mode="HTML"
            )
            return

        await db.add_order(user_id, product_id, cost, resolution)
        await msg.answer(
            f"✅ <b>Ruxsat berildi!</b>\n\n"
            f"📱 Telefon: <code>{contact}</code>\n"
            f"🎬 Film: <b>{product_title}</b>\n"
            f"📺 Sifat: <b>{resolution.upper()}</b>\n"
            f"💰 To'lov: <b>{format_price(cost)} so'm</b>",
            reply_markup=admin_button,
            parse_mode="HTML"
        )
        await state.clear()
        return

    # ==================== HAMMA FILMLAR ====================
    all_products = await db.get_active_products()
    all_product_ids = [p[0] for p in all_products]
    total_films = len(all_product_ids)

    # Yangi foydalanuvchi
    if not user_info:
        await db.add_user_by_admin(contact, cost, all_product_ids, resolution)
        await msg.answer(
            f"✅ <b>Muvaffaqiyatli!</b>\n\n"
            f"📱 Telefon: <code>{contact}</code>\n"
            f"🎬 Filmlar: <b>{total_films} ta</b>\n"
            f"📺 Sifat: <b>{resolution.upper()}</b>\n"
            f"💰 To'lov: <b>{format_price(cost)} so'm</b>",
            reply_markup=admin_button,
            parse_mode="HTML"
        )
        await state.clear()
        return

    # Mavjud foydalanuvchi - faqat yangi filmlar
    user_id = user_info[0]
    user_products = set(p[0] for p in await db.get_user_paid_orders(user_id, resolution))
    new_products = [pid for pid in all_product_ids if pid not in user_products]

    if not new_products:
        await msg.answer(
            f"ℹ️ Bu foydalanuvchiga barcha filmlarga {resolution.upper()} "
            "sifatda allaqachon ruxsat berilgan!",
            reply_markup=admin_button
        )
        await state.clear()
        return

    for product_id in new_products:
        await db.add_order(user_id, product_id, cost / len(new_products), resolution)

    await msg.answer(
        f"✅ <b>Ruxsat berildi!</b>\n\n"
        f"📱 Telefon: <code>{contact}</code>\n"
        f"🎬 Yangi filmlar: <b>{len(new_products)} ta</b>\n"
        f"📺 Sifat: <b>{resolution.upper()}</b>\n"
        f"💰 To'lov: <b>{format_price(cost)} so'm</b>",
        reply_markup=admin_button,
        parse_mode="HTML"
    )
    await state.clear()


def format_price(price):
    return f"{int(price):,}".replace(',', ' ')