from aiogram.fsm.state import State,StatesGroup

class TaskForm(StatesGroup):
    title = State()
    time = State()
    assignee = State()
    status = State()
    change_time = State()
    change_title = State()
    change_assignee = State()