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

    user_ids = [user[0] for user in user_row]
    all_films = []
    for user_id in user_ids:
        films = await db.get_user_unique_films(user_id)
        if films:
            all_films.extend(films)


    seen = set()
    unique_films = []
    for film in all_films:
        if film[1] not in seen:
            seen.add(film[1])
            unique_films.append(film)

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

    product = await db.get_product_by_name(film_name)
    if not product:
        return

    product_id = product[0]
    await state.update_data(selected_product_id=product_id, selected_product_name=film_name)


    user_row = await db.get_user_by_tg_id(msg.from_user.id)
    user_ids = [user[0] for user in user_row]
    purchased_resolutions = []
    for user_id in user_ids:
        res = await db.get_user_purchased_resolutions(user_id, product_id)
        purchased_resolutions.extend(res)


    purchased_resolutions = list(set(purchased_resolutions))

    await msg.answer(
        f"<b>{film_name}</b>\n\n"
        "Qaysi sifatda tomosha qilishni xohlaysiz?",
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
    user_ids = [user[0] for user in user_row]
    existing_order = ()
    for user_id in user_ids:
        result = await db.get_user_order(user_id, product_id, resolution)
        if result:
            existing_order = result
            break

    product = await db.get_product(product_id)

    if existing_order:

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

        await call.message.answer(
            f"❌ Siz <b>{product[1]}</b> filmini {resolution.upper()} sifatda hali sotib olmagansiz.\n\n"
            "Sotib olish uchun 🎬 Filmlar bo'limiga o'ting.",
            reply_markup=user_buttons,
            parse_mode='HTML'
        )
        await state.clear()

    await call.answer()