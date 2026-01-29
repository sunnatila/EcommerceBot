from aiogram.filters import StateFilter
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from keyboards.default import user_buttons, user_orders_keyboard
from keyboards.inline import group_link_button, my_film_resolution_buttons
from loader import db, dp


@dp.message(lambda msg: msg.text == "🎞 Mening Filmlarim")
async def send_user_products(msg: Message, state: FSMContext):
    await state.clear()
    user_row = await db.get_user_by_tg_id(msg.from_user.id)
    if not user_row:
        await msg.answer("Sizda hali sotib olingan filmlar yo'q.", reply_markup=user_buttons)
        return

    user_id = user_row[0]

    # Foydalanuvchi sotib olgan UNIKAL filmlar (resolution'siz)
    unique_films = await db.get_user_unique_films(user_id)

    if not unique_films:
        await msg.answer("Sizda hali sotib olingan filmlar yo'q.", reply_markup=user_buttons)
        return

    await msg.answer("Sizning film kolleksiyangiz:", reply_markup=await user_orders_keyboard(unique_films))
    await state.set_state("my_films_select")


@dp.message(StateFilter("my_films_select"), lambda msg: msg.text == "🔙 Ortga")
async def back_from_my_films(msg: Message, state: FSMContext):
    await msg.answer("Kerakli bo'limni tanlang 😊", reply_markup=user_buttons)
    await state.clear()


@dp.message(StateFilter("my_films_select"))
async def select_film_from_my_films(msg: Message, state: FSMContext):
    film_name = msg.text.strip()

    # Filmni topish
    product = await db.get_product_by_name(film_name)
    if not product:
        return

    product_id = product[0]
    await state.update_data(selected_product_id=product_id, selected_product_name=film_name)

    # Foydalanuvchi qaysi resolution'larda sotib olganini tekshirish
    user_row = await db.get_user_by_tg_id(msg.from_user.id)
    user_id = user_row[0]

    purchased_resolutions = await db.get_user_purchased_resolutions(user_id, product_id)

    await msg.answer(
        f"📺 <b>{film_name}</b>\n\n"
        "Qaysi sifatda tomosha qilmoqchisiz?",
        reply_markup=my_film_resolution_buttons(product_id, purchased_resolutions),
        parse_mode='HTML'
    )



@dp.callback_query(lambda call: call.data.startswith('myfilm_'))
async def select_resolution_my_film(call: CallbackQuery, state: FSMContext):
    parts = call.data.split('_')
    product_id = int(parts[1])
    resolution = parts[2]

    await call.message.delete()

    user_row = await db.get_user_by_tg_id(call.from_user.id)
    user_id = user_row[0]

    # Bu resolution'da sotib olganmi?
    existing_order = await db.get_user_order(user_id, product_id, resolution)
    product = await db.get_product(product_id)

    if existing_order:
        # Sotib olgan - guruh linkini berish
        if resolution == "4k":
            group_url = product[8]
        else:
            group_url = product[7]

        await call.message.answer(
            f"✅ <b>{product[1]}</b> - {resolution.upper()}\n\n"
            "Kinoni ko'rish uchun quyidagi tugmani bosing 👇",
            reply_markup=await group_link_button(group_url),
            parse_mode='HTML',
            protect_content = True,
        )
    else:
        # Sotib olmagan
        await call.message.answer(
            f"❌ Siz <b>{product[1]}</b> filmini {resolution.upper()} sifatda hali sotib olmagansiz.\n\n"
            "Sotib olish uchun 🎬 Filmlar bo'limiga o'ting.",
            reply_markup=user_buttons,
            parse_mode='HTML'
        )
        await state.clear()

    await call.answer()