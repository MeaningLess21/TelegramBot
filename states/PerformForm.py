from aiogram.fsm.state import State,StatesGroup

class PerformForm(StatesGroup):
    start = State()
    name = State()
    id = State()
    change_id = State()
    change_name = State()
