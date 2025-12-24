from aiogram.fsm.state import State, StatesGroup


class GroupStates(StatesGroup):
    group_name = State()
    group_description = State()
    group_paid = State()
    group_price = State()
    group_url = State()
    group_status = State()
    group_video = State()
    group_save = State()

