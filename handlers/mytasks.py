from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from DB.connect import tasks_collection


router = Router()

@router.message(Command("my_tasks"))
async def cmd_tasks(message: Message, state: FSMContext):
    tasks_count = tasks_collection.count_documents({})
    if tasks_count > 0:
        response = "Список ваших задач:\n"
        tasks = tasks_collection.find({'assignee_id':message.from_user.id})
        for task in tasks:
            response += f"ID Задачи: {task['id']}\n" \
                        f"Задача: {task['title']}\n" \
                        f"Время: {task['time']}\n" \
                        f"Исполнитель: {task['assignee']}\n" \
                        f"Примечание: {task['note']}\n" \
                        f"Статус: {task['status']}\n" \
                        f"------------------------\n"
    else:
        response = "Нет доступных задач."

    await message.reply(response)