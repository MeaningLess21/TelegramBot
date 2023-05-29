from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.utils.markdown import hbold,hunderline,hcode,hitalic
from DB.connect import tasks_collection


router = Router()

@router.message(Command("tasks"))
async def cmd_tasks(message: Message, state: FSMContext):
    tasks_count = tasks_collection.count_documents({})
    if tasks_count > 0:
        response = hunderline("Список задач:\n")
        tasks = tasks_collection.find()
        for task in tasks:
            response += f"{hbold('ID Задачи:')} {hitalic(task['id'])}\n" \
                        f"Задача: {task['title']}\n" \
                        f"{hcode('Время:') }{hitalic(task['time'])}\n" \
                        f"{hunderline('Исполнитель:')} {task['assignee']}\n" \
                        f"{hitalic('Примечание:')} {task['note']}\n" \
                        f"Статус: {task['status']}\n" \
                        f"----------------------------------------------------\n"
    else:
        response = "Нет доступных задач."

    await message.reply(response)