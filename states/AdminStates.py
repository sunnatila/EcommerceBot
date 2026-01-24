from aiogram.fsm.state import State, StatesGroup


class GroupStates(StatesGroup):
    film_name = State()
    film_description = State()
    film_paid = State()

    # 1080p uchun
    film_price_1080p = State()
    film_url_1080p = State()

    # 4K uchun
    film_price_4k = State()
    film_url_4k = State()

    film_status = State()
    film_video = State()
    film_save = State()