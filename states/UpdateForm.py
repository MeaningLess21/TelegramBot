from aiogram.fsm.state import State,StatesGroup

class UpdateForm(StatesGroup):
    id = State()
    title = State()
    time = State()
    assignee = State()
    note = State()
    status = State()