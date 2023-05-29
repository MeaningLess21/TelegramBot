from aiogram import Router,types
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton,InlineKeyboardMarkup
from aiogram.types import Message
from aiogram.filters import Text
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from states.TaskForm import TaskForm
from DB.connect import db,tasks_collection,performers_collection
from datetime import datetime,timedelta

router = Router()
current_date = datetime.now().date()

async def check_time(message):
    try:
        time = message.split(':')
        if len(time)==2 and int(time[0])<24 and int(time[1])<60:
            return True
        else:
            return False
    except:
        return False

@router.callback_query(Text(startswith= 'chn_'))
async def callbacks_task(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.split('_')[1]
    await callback.message.edit_text(text=callback.message.text)
    if action == 'title':
        await state.set_state(TaskForm.change_title)
        await callback.message.answer("Напишите новый заголовок")
    if action == 'time':
        await state.set_state(TaskForm.change_time)
        buttons = []
        for i in range(3):
            buttons.append([InlineKeyboardButton(text=str(current_date + timedelta(days=i)),
                                                 callback_data=str(current_date + timedelta(days=i)))])
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)
        await callback.message.answer('Выберите дату выполнения задачи', reply_markup=markup)
    if action == 'assignee':
        await state.set_state(TaskForm.change_assignee)
        if performers_collection.count_documents({})>0:
            assignees = performers_collection.find()
            buttons = []
            for assignee in assignees:
                buttons.append(
                    [InlineKeyboardButton(text=assignee.get('FIO'), callback_data='assignee_' + str(assignee.get('id')))])
            markup = InlineKeyboardMarkup(inline_keyboard=buttons)
            await callback.message.answer('Выберите кто выполнять будет задачу', reply_markup=markup)
        else:
            await state.clear()
            await callback.message.answer('Нет исполнителей\n'
                                          'Добавте нового исполнителя')
    if action == 'note':
        await state.set_state(TaskForm.assignee)
        await callback.message.answer("Напишите новое примечание")

@router.callback_query(Text(startswith= 'assignee_'))
async def callbacks_asignee(callback: types.CallbackQuery, state: FSMContext):
    id = int(callback.data.split('_')[1])
    await state.update_data(assignee_id = id)
    performers = db['performers']
    assignee = performers.find_one({'id':int(id)})
    await state.update_data(assignee_task = assignee.get('FIO'))
    if not await state.get_state() == TaskForm.change_assignee:
        await state.set_state(TaskForm.assignee)
        await callback.message.edit_text(f"Исполнитель - {assignee.get('FIO')}")
        await callback.message.answer(f"Напишите примечание к задаче")
    else:
        data = await state.get_data()
        await callback.message.answer(f'Ваша задача:\n'
                             f'Заголовок - {data["title_task"]}\n'
                             f'Время выполнения - {data["time_task"]}\n'
                             f'Исполнитель - {data["assignee_task"]}\n'
                             f'Примечание - {data["note"]}')
        buttons = [
            [InlineKeyboardButton(text="Да, создаем задачу", callback_data='task_create')],
            [InlineKeyboardButton(text="Нет,хочу отредактировать", callback_data='task_change')]
        ]
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)
        await callback.message.answer("Задача корректна?", reply_markup=markup)
@router.callback_query(Text(startswith= 'task_'))
async def callbacks_task(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.split('_')[1]
    await state.update_data(status_task='Создана')
    data = await state.get_data()
    if action =='create':
        last_document = tasks_collection.find_one({}, sort=[('_id', -1)])
        try:
            last_id =last_document.get('id')
        except:
            last_id = 0
        task = {
            'id': last_id + 1,
            'title': data["title_task"],
            'time': data["time_task"],
            'assignee': data["assignee_task"],
            'assignee_id': data["assignee_id"],
            'note': data["note"],
            'status': data['status_task']
        }
        tasks_collection.insert_one(task)
        await callback.message.edit_text("Задача создана")
        await state.clear()
    if action == 'change':
        buttons = [
            [InlineKeyboardButton(text="Заголовок", callback_data='chn_title')],
            [InlineKeyboardButton(text="Время", callback_data='chn_time')],
            [InlineKeyboardButton(text="Исполнитель", callback_data='chn_assignee')],
            [InlineKeyboardButton(text="Примечание", callback_data='chn_note')]
        ]
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)
        await callback.message.edit_text("Что вы хотите изменить?", reply_markup=markup)
@router.callback_query(Text(startswith= f'2023-{str(current_date).split("-")[1]}-'))
async def callbacks_day(callback: types.CallbackQuery, state: FSMContext):
    await state.update_data(time_task=callback.data)
    await callback.message.edit_text("Введите время выполнения задачи в формате (H:M): ")
    print(await state.get_state())
    if not await state.get_state() == TaskForm.change_time:
        await state.set_state(TaskForm.time)

@router.message(Command("add_task"))
async def cmd_add_task(message: Message, state: FSMContext):
    button = [
        [KeyboardButton(text='Назад')]
    ]
    markup = ReplyKeyboardMarkup(keyboard=button, resize_keyboard=True)
    await message.answer('Введите заголовок задачи', reply_markup=markup)
    await state.set_state(TaskForm.title)

@router.message(TaskForm.title)
async def process_title(message: Message, state: FSMContext):
    print(message)
    if message.entities != None:
        await state.clear()
        await message.answer('Действие отменено')
    else:
        await state.update_data(title_task= message.text)
        buttons = []
        for i in range(3):
             buttons.append([InlineKeyboardButton(text=str(current_date + timedelta(days=i)),callback_data=str(current_date+timedelta(days=i)))])
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)
        await message.answer('Выберите дату выполнения задачи', reply_markup=markup)
@router.message(TaskForm.time)
async def process_time(message: Message, state: FSMContext):
    data = await state.get_data()
    if message.entities != None:
        await state.clear()
        await message.answer('Действие отменено')
    else:
        if await check_time(message.text):
            await state.update_data(time_task= data["time_task"] + ' '+ message.text)
            if performers_collection.count_documents({}) > 0:
                assignees = performers_collection.find()
                buttons =[]
                for assignee in assignees:
                    buttons.append([InlineKeyboardButton(text= assignee.get('FIO'), callback_data = 'assignee_'+str(assignee.get('id')))])
                markup = InlineKeyboardMarkup(inline_keyboard=buttons)
                await message.answer('Выберите кто выполнять будет задачу', reply_markup=markup)
            else:
                await state.clear()
                await message.answer('Нет исполнителей\n'
                                              'Добавте нового исполнителя')
        else:
            await message.answer("Введен некорктный формат времени\n"
                                 "Введите время в формате H:M")
@router.message(TaskForm.assignee)
async def process_assignee(message: Message, state: FSMContext):
    if message.entities != None:
        await state.clear()
        await message.answer('Действие отменено')
    else:
        await state.update_data(note = message.text)
        data = await state.get_data()
        await message.answer(f'Ваша задача:\n'
                             f'Заголовок - {data["title_task"]}\n'
                             f'Время выполнения - {data["time_task"]}\n'
                             f'Исполнитель - {data["assignee_task"]}\n'
                             f'Примечание - {data["note"]}')
        buttons = [
            [InlineKeyboardButton(text = "Да, создаем задачу",callback_data = 'task_create')],
            [InlineKeyboardButton(text = "Нет,хочу отредактировать",callback_data = 'task_change')]
        ]
        markup = InlineKeyboardMarkup(inline_keyboard = buttons)
        await message.answer("Задача корректна?", reply_markup= markup)




@router.message(TaskForm.change_title)
async def change_title(message:Message, state: FSMContext):
    await state.update_data(title_task=message.text)
    data = await state.get_data()
    await message.answer(f'Ваша задача:\n'
                         f'Заголовок - {data["title_task"]}\n'
                         f'Время выполнения - {data["time_task"]}\n'
                         f'Исполнитель - {data["assignee_task"]}\n'
                         f'Примечание - {data["note"]}')
    buttons = [
        [InlineKeyboardButton(text="Да, создаем задачу", callback_data='task_create')],
        [InlineKeyboardButton(text="Нет,хочу отредактировать", callback_data='task_change')]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("Задача корректна?", reply_markup=markup)


@router.message(TaskForm.change_time)
async def change_time(message:Message, state: FSMContext):
    data = await state.get_data()
    if await check_time(message.text):
        await state.update_data(time_task=data["time_task"] + ' '+ message.text)
        data = await state.get_data()
        await message.answer(f'Ваша задача:\n'
                             f'Заголовок - {data["title_task"]}\n'
                             f'Время выполнения - {data["time_task"]}\n'
                             f'Исполнитель - {data["assignee_task"]}\n'
                             f'Примечание - {data["note"]}')
        buttons = [
            [InlineKeyboardButton(text="Да, создаем задачу", callback_data='task_create')],
            [InlineKeyboardButton(text="Нет,хочу отредактировать", callback_data='task_change')]
        ]
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)
        await message.answer("Задача корректна?", reply_markup=markup)

    else:
        await message.answer("Введен некорктный формат времени\n"
                         "Введите время в формате H:M")

