from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton


# ==================== BITTA FILM UCHUN ====================

async def user_product_buttons(product_id, resolution, price):
    """Bitta film uchun tugmalar - callback_data ichida barcha ma'lumotlar"""
    return InlineKeyboardBuilder(
        markup=[
            [
                # buy_{product_id}_{resolution}_{price}
                InlineKeyboardButton(text="Sotib olish", callback_data=f"buy_{product_id}_{resolution}_{price}"),
                InlineKeyboardButton(text="Sovg'a qilish 🎁", callback_data="present_product"),
            ]
        ]
    ).adjust(2).as_markup()


def get_payment_buttons(product_id, resolution, price):
    """To'lov usullarini tanlash - callback_data ichida barcha ma'lumotlar"""
    return InlineKeyboardBuilder(
        markup=[
            # ====== FROZEN: Click va PayMe vaqtinchalik o'chirilgan ======
            # [
            #     # pay_{method}_{product_id}_{resolution}_{price}
            #     InlineKeyboardButton(text="💳 Click", callback_data=f"pay_click_{product_id}_{resolution}_{price}"),
            #     InlineKeyboardButton(text="💳 PayMe", callback_data=f"pay_payme_{product_id}_{resolution}_{price}"),
            # ],
            [
                InlineKeyboardButton(text="To'lov qilish", callback_data=f"pay_other_{product_id}_{resolution}_{price}"),
            ]
        ]
    ).as_markup()


# ==================== HAMMA FILMLAR UCHUN ====================

async def all_pr_buy_buttons(products_str, resolution, price):
    """Hamma filmlar uchun sotib olish tugmasi"""
    # allbuy_{products_str}_{resolution}_{price}
    return InlineKeyboardBuilder(
        markup=[
            [InlineKeyboardButton(text="Sotib olish", callback_data=f"allbuy_{products_str}_{resolution}_{price}")]
        ]
    ).adjust(1).as_markup()


def get_all_payment_buttons(products_str, resolution, price):
    """Hamma filmlar uchun to'lov usullari"""
    return InlineKeyboardBuilder(
        markup=[
            # ====== FROZEN: Click va PayMe vaqtinchalik o'chirilgan ======
            # [
            #     # allpay_{method}_{products_str}_{resolution}_{price}
            #     InlineKeyboardButton(text="💳 Click", callback_data=f"allpay_click_{products_str}_{resolution}_{price}"),
            #     InlineKeyboardButton(text="💳 PayMe", callback_data=f"allpay_payme_{products_str}_{resolution}_{price}"),
            # ],
            [
                InlineKeyboardButton(text="To'lov qilish", callback_data=f"allpay_other_{products_str}_{resolution}_{price}"),
            ]
        ]
    ).as_markup()


# ==================== RESOLUTION TANLASH ====================

async def resolution_buttons(pr_id):
    buttons = InlineKeyboardBuilder(
    markup=[
        [
            InlineKeyboardButton(text="📺 1080p", callback_data=f"res_1080p_{pr_id}"),
            InlineKeyboardButton(text="📺 4K", callback_data=f"res_4k_{pr_id}"),
        ]
    ]
    ).adjust(2).as_markup()
    return buttons


all_resolution_buttons = InlineKeyboardBuilder(
    markup=[
        [
            InlineKeyboardButton(text="📺 1080p", callback_data="all_res_1080p"),
            InlineKeyboardButton(text="📺 4K", callback_data="all_res_4k"),
        ]
    ]
).adjust(2).as_markup()


# ==================== BOSHQA TUGMALAR ====================

async def group_link_button(link):
    return InlineKeyboardBuilder(
        markup=[
            [InlineKeyboardButton(text="👉 Guruhga qo'shilish 👈", url=link)]
        ]
    ).adjust(1).as_markup()


async def sent_payment_url(data: dict):
    from product.views import send_link_for_payment
    result = await send_link_for_payment(data)
    payment_url = result.get('payment_url')
    return InlineKeyboardBuilder(
        markup=[
            [InlineKeyboardButton(text="To'lovga o'tish", url=payment_url)]
        ]
    ).adjust(1).as_markup()


def my_film_resolution_buttons(product_id, purchased_resolutions):
    """Mening filmlarim - resolution tanlash tugmalari

    purchased_resolutions: ['1080p', '4k'] yoki ['1080p'] yoki ['4k'] yoki []
    """
    buttons = []

    # 1080p tugmasi
    if '1080p' in purchased_resolutions:
        text_1080p = "📺 1080p ✅"
    else:
        text_1080p = "📺 1080p ❌"
    buttons.append(InlineKeyboardButton(text=text_1080p, callback_data=f"myfilm_{product_id}_1080p"))

    # 4K tugmasi
    if '4k' in purchased_resolutions:
        text_4k = "📺 4K ✅"
    else:
        text_4k = "📺 4K ❌"
    buttons.append(InlineKeyboardButton(text=text_4k, callback_data=f"myfilm_{product_id}_4k"))

    return InlineKeyboardBuilder(markup=[buttons]).adjust(2).as_markup()

