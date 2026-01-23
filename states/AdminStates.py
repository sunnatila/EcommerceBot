from aiogram.fsm.state import State, StatesGroup


class GroupStates(StatesGroup):
    film_name = State()
    film_description = State()
    film_paid = State()
    film_price = State()
    film_url = State()
    film_status = State()
    film_video = State()
    film_save = State()

