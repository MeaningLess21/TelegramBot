from aiogram.fsm.state import State,StatesGroup

class DeleteForm(StatesGroup):
    id = State()
    assignee = State()