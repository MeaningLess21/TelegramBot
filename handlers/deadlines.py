import asyncio
import config
from DB.connect import tasks_collection
from main import bot
from datetime import datetime,timedelta

tasks_ids=[]
async def check_task_deadlines():
    global tasks_ids
    tasks_ids.clear()
    for task in tasks_collection.find():
        tasks_ids.append(task["id"])
    while True:
        tasks = tasks_collection.find()
        current_time = datetime.now()
        for task in tasks:
            deadline = task.get('time')
            deadline = datetime.strptime(deadline, '%Y-%m-%d %H:%M')
            update_time = deadline - timedelta(hours=1)
            if deadline and current_time > deadline:
                # Задача истекла по времени, выполняем необходимые действия
                task_title = task.get('title')
                assignee = task.get('assignee')
                if task_title and \
                        assignee and \
                        (task.get('status').lower() != "выполнена" and task.get('status').lower() != "неактуальна"):
                    message = f"Задача '{task_title}' истекла по времени. Исполнитель: {assignee}"
                    await bot.send_message(chat_id=config.admin_id, text=message)
                    await bot.send_message(chat_id=task.get('assignee_id'), text=message)
            elif current_time > update_time:
                task_title = task.get('title')
                assignee = task.get('assignee')
                message = f'Задача "{task_title}" истечет менее чем через час. Исполнитель: {assignee}'
                await bot.send_message(chat_id=task.get('assignee_id'), text=message)
            # Пауза перед следующей проверкой
        await asyncio.sleep(3600)  # Проверяем каждый час

async def check_new_tasks():
    global tasks_ids
    while True:
        new_tasks = tasks_collection.find()
        for task in new_tasks:
            task_id = task['id']
            if task_id in tasks_ids:
                continue
            else:
                message = f'У Вас новая задача\n' \
                          f'Задача: {task["title"]}\n' \
                          f'Время: {task["time"]}\n' \
                          f'Примечание: {task["note"]}\n' \
                          f'Статус: {task["status"]}'
                await bot.send_message(chat_id=task["assignee_id"],text=message)
                tasks_ids.append(task["id"])
        await asyncio.sleep(60)

