from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.default import admin_button, get_users_panel_buttons, get_products_for_admin
from .start import AdminFilter
from loader import db, dp


@dp.message(AdminFilter(), lambda msg: msg.text == "👤 Foydalanuvchilar bo'limi")
async def send_users_panel(msg: Message, state: FSMContext):
    await msg.answer("Foydalanuvchilar bo'limidan kerak bo'lgan tugmachani bo'sing:", reply_markup=get_users_panel_buttons)



@dp.message(AdminFilter(), lambda msg: msg.text == '🔙 Ortga')
async def back_to_menu(msg: Message, state: FSMContext):
    await msg.answer("Iltimos, kerakli kategoriyani tanlang 😊", reply_markup=admin_button)


@dp.message(AdminFilter(), lambda msg: msg.text == '👤 Foydalanuvchiga film qo\'shish')
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
            "Iltimos, foydalanuvchini telefon raqamini qaytadan kiriting (namuna: +99890xxxxxxx yoki 90xxxxxxx).\n"
            "Yoki kontaktini jonating"
        )
        return

    await state.update_data(contact=text)
    await msg.answer("To'langan summani kiriting: ")
    await state.set_state("get_paid_sum")


@dp.message(AdminFilter(), StateFilter("get_paid_sum"))
async def get_paid_sum(msg: Message, state: FSMContext):
    text = msg.text
    if text.isdigit():
        await state.update_data(cost=float(text))
        await msg.answer("Qaysi filmga ruxsat bermoqchisiz?", reply_markup=await get_products_for_admin())
        await state.set_state("groups_get")
    else:
        await msg.answer("Faqat raqam kirita olasiz!")


@dp.message(AdminFilter(), StateFilter("groups_get"))
async def groups_get(msg: Message, state: FSMContext):
    data = await state.get_data()
    contact = data.get("contact")
    cost = data.get("cost")
    text = msg.text
    await state.clear()

    user_info = await db.get_user_by_phone(contact)

    # Bitta film tanlanganda
    if text != "Hamma filmlarga ruxsat berish":
        product = await db.get_product_by_name(text)
        if not product:
            await msg.answer(
                "❌ <b>Xatolik!</b>\n\n"
                "Bunday film topilmadi.\n"
                "Iltimos, mavjud filmlardan birini tanlang.",
                parse_mode="HTML"
            )
            await state.update_data(contact=contact, cost=cost)
            await state.set_state("groups_get")
            return

        product_id = product[0]
        product_title = product[1]

        # Yangi foydalanuvchi
        if not user_info:
            await db.add_user_by_admin(contact, cost, [product_id])
            await msg.answer(
                "✅ <b>Muvaffaqiyatli!</b>\n\n"
                f"📱 Telefon: <code>{contact}</code>\n"
                f"🎬 Film: <b>{product_title}</b>\n"
                f"💰 To'lov: <b>{format_price(cost)} so'm</b>\n\n"
                "Yangi foydalanuvchi qo'shildi va filmga ruxsat berildi! 🎉",
                reply_markup=admin_button,
                parse_mode="HTML"
            )
            return

        # Mavjud foydalanuvchi
        user_id = user_info[0]
        user_product = await db.get_user_order(user_id, product_id)

        if user_product:
            await msg.answer(
                "⚠️ <b>Diqqat!</b>\n\n"
                f"📱 Telefon: <code>{contact}</code>\n"
                f"🎬 Film: <b>{product_title}</b>\n\n"
                "Bu foydalanuvchiga ushbu filmga allaqachon ruxsat berilgan!\n"
                "Iltimos, boshqa film tanlang yoki boshqa foydalanuvchi qo'shing.",
                parse_mode="HTML"
            )
            await state.update_data(contact=contact, cost=cost)
            await state.set_state("groups_get")
            return

        await db.add_order(user_id, product_id, cost)
        await msg.answer(
            "✅ <b>Ruxsat berildi!</b>\n\n"
            f"📱 Telefon: <code>{contact}</code>\n"
            f"🎬 Film: <b>{product_title}</b>\n"
            f"💰 To'lov: <b>{format_price(cost)} so'm</b>\n\n"
            "Foydalanuvchiga filmga muvaffaqiyatli ruxsat berildi! 🎬",
            reply_markup=admin_button,
            parse_mode="HTML"
        )
        return

    # Hamma filmlarga ruxsat berish
    all_products = await db.get_active_products()
    all_product_ids = [group[0] for group in all_products]
    total_films = len(all_product_ids)

    # YANGI FOYDALANUVCHI
    if not user_info:
        await db.add_user_by_admin(contact, cost, all_product_ids)
        await msg.answer(
            "✅ <b>Muvaffaqiyatli bajarildi!</b>\n\n"
            f"📱 Telefon: <code>{contact}</code>\n"
            f"🎬 Filmlar soni: <b>{total_films} ta</b>\n"
            f"💰 To'lov: <b>{format_price(cost)} so'm</b>\n\n"
            "🎉 Yangi foydalanuvchi qo'shildi va barcha filmlarga ruxsat berildi!",
            reply_markup=admin_button,
            parse_mode="HTML"
        )
        return

    # MAVJUD FOYDALANUVCHI - faqat yangi filmlarga
    user_id = user_info[0]
    user_products = set(product[0] for product in (await db.get_user_paid_orders(user_id)))
    new_products = [pid for pid in all_product_ids if pid not in user_products]

    if not new_products:
        await msg.answer(
            "ℹ️ <b>Ma'lumot</b>\n\n"
            f"📱 Telefon: <code>{contact}</code>\n"
            f"🎬 Jami filmlar: <b>{total_films} ta</b>\n\n"
            "Bu foydalanuvchiga barcha filmlarga allaqachon ruxsat berilgan!\n"
            "Yangi filmlar qo'shing yoki boshqa foydalanuvchi tanlang.",
            reply_markup=admin_button,
            parse_mode="HTML"
        )
        return

    # Yangi filmlarga ruxsat berish (bulk yoki bitta-bitta)
    if len(new_products) == 1:
        await db.add_order(user_id, new_products[0], cost)
    else:
        # Agar bulk metod mavjud bo'lsa
        # await db.add_orders_bulk(user_id, new_products, cost)
        # Aks holda:
        for product_id in new_products:
            await db.add_order(user_id, product_id, cost)

    already_count = len(user_products)
    await msg.answer(
        "✅ <b>Ruxsat berildi!</b>\n\n"
        f"📱 Telefon: <code>{contact}</code>\n"
        f"🎬 Yangi filmlar: <b>{len(new_products)} ta</b>\n"
        f"📊 Oldingi filmlar: <b>{already_count} ta</b>\n"
        f"📈 Jami: <b>{len(new_products) + already_count} ta</b>\n"
        f"💰 To'lov: <b>{format_price(cost)} so'm</b>\n\n"
        "🎉 Foydalanuvchiga yangi filmlarga muvaffaqiyatli ruxsat berildi!",
        reply_markup=admin_button,
        parse_mode="HTML"
    )



def format_price(price):
    """Narxni bo'sh joy bilan formatlash: 50000 -> 50 000"""
    return f"{int(price):,}".replace(',', ' ')