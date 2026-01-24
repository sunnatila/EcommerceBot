from aiogram.fsm.state import State, StatesGroup


class ProductStates(StatesGroup):
    products_page = State()
    select_resolution = State()
    select_resolution_all = State()
