from aiogram.fsm.state import State, StatesGroup


class ProductStates(StatesGroup):
    products_page = State()
    product_info = State()
    product_payment = State()
    payment_confirm = State()
