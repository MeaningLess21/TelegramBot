from aiogram import Router,types
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton,InlineKeyboardMarkup
from aiogram.types import Message
from aiogram.filters import Text
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from states.UpdateForm import UpdateForm
from DB.connect import db,tasks_collection
from datetime import datetime,timedelta
from handlers.newtask import check_time

router = Router()
current_date = datetime.now().date()


@router.callback_query(Text(startswith= 'new_as_'))
async def callbacks_update_assignee(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text=callback.message.text)
    id = int(callback.data.split('_')[2])
    data = await state.get_data()
    performers = db['performers']
    assignee = performers.find_one({'id': int(id)})
    filter = {'id': data['id']}
    update = {'$set': {'assignee_id': id,'assignee':assignee.get('FIO')}}
    tasks_collection.update_one(filter, update)
    await callback.message.answer("Исполнитель задачи изменен ")
    await state.clear()


@router.callback_query(Text(startswith= 't_'))
async def callbacks_update_time(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(text=callback.message.text)
    time= callback.data.split("_")[1]
    await state.update_data(time = time)
    await state.set_state(UpdateForm.time)
    await callback.message.answer("Введите время выполнения задачи")



@router.callback_query(UpdateForm.status)
async def callbacks_update_status(callback: types.CallbackQuery, state: FSMContext):
    action =callback.data
    await callback.message.edit_text(callback.message.text)
    data = await state.get_data()
    filter = {'id': data['id']}
    if action == 'create':
        update = {'$set': {'status': 'Создана'}}
        tasks_collection.update_one(filter, update)
        await callback.message.answer("Статус задачи изменен на 'В процессе'")
        await state.clear()
    if action == 'progress':
        update = {'$set': {'status': 'В процессе'}}
        tasks_collection.update_one(filter, update)
        await callback.message.answer("Статус задачи изменен на 'В процессе'")
        await state.clear()
    if action == 'done':
        update = {'$set': {'status': 'Выполнена'}}
        tasks_collection.update_one(filter, update)
        await callback.message.answer("Статус задачи изменен на 'Выполнена'")
        await state.clear()
    if action == 'irrelevant':
        update = {'$set': {'status': 'Неактуальна'}}
        tasks_collection.update_one(filter, update)
        await callback.message.answer("Статус задачи изменен на 'Неактуальна'")
        await state.clear()

@router.callback_query(Text(startswith= 'upd_'))
async def callbacks_update(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.split('_')[1]
    await callback.message.edit_text(text=callback.message.text)
    if action == 'status':
        await state.set_state(UpdateForm.status)
        buttons = [
            [InlineKeyboardButton(text="Создана", callback_data='create')],
            [InlineKeyboardButton(text="В процессе", callback_data='progress')],
            [InlineKeyboardButton(text="Выполнена", callback_data='done')],
            [InlineKeyboardButton(text="Неактуальна", callback_data='irrelevant')]
        ]
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)
        await callback.message.answer('Выберите новый статус задачи',reply_markup=markup)
    if action == 'title':
        await state.set_state(UpdateForm.title)
        await callback.message.answer("Введите новый заголок задачи")
    if action == 'note':
        await state.set_state(UpdateForm.note)
        await callback.message.answer("Введите новое примечание задачи")
    if action == 'time':
        await state.set_state(UpdateForm.time)
        buttons = []
        for i in range(3):
            buttons.append([InlineKeyboardButton(text=str(current_date + timedelta(days=i)),
                                                 callback_data='t_'+str(current_date + timedelta(days=i)))])
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)
        await callback.message.answer("Выберите новую дату задачи",reply_markup=markup)
    if action == 'assignee':
        await state.set_state(UpdateForm.assignee)
        assignees = db['performers'].find()
        buttons = []
        for assignee in assignees:
            buttons.append(
                [InlineKeyboardButton(text=assignee.get('FIO'), callback_data='new_as_' + str(assignee.get('id')))])
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)
        await callback.message.answer("Выбери нового исполнителя задачи",reply_markup=markup)

@router.message(Command("update_task"))
async def cmd_upd_task(message: Message, state: FSMContext):
    button= [
        [KeyboardButton(text='Назад')]
    ]
    markup = ReplyKeyboardMarkup(keyboard = button,resize_keyboard=True)
    await message.answer('Введите ID задачи',reply_markup=markup)
    await state.set_state(UpdateForm.id)

@router.message(UpdateForm.id)
async def process_id(message: Message, state: FSMContext):
    if message.text.isdigit():
        id = int(message.text)
        await state.update_data(id=id)
        try:
            task = tasks_collection.find_one({'id':id})
            response = "Что вы хотите изменить в задаче?\n" \
                       f"Задача: {task['title']}\n" \
                       f"Время: {task['time']}\n" \
                       f"Исполнитель: {task['assignee']}\n" \
                       f"Примечание: {task['note']}\n" \
                       f"Статус: {task['status']}\n"
            buttons = [
                [InlineKeyboardButton(text = "Заголовок",callback_data = 'upd_title')],
                [InlineKeyboardButton(text = "Время",callback_data = 'upd_time')],
                [InlineKeyboardButton(text = "Исполнитель",callback_data = 'upd_assignee')],
                [InlineKeyboardButton(text = "Примечание",callback_data = 'upd_note')],
                [InlineKeyboardButton(text = "Статус",callback_data = 'upd_status')]
            ]
            markup = InlineKeyboardMarkup(inline_keyboard = buttons)
            await message.answer(response,reply_markup=markup)
        except:
            await message.answer("Задачи по такому ID нет")
    else:
        await message.answer("ID должно быть численным значением")
        await state.set_state(UpdateForm.id)
        await message.answer("Введи ID задачи")

@router.message(UpdateForm.title)
async def upd_title(message: Message, state: FSMContext):
    data = await state.get_data()
    filter = {'id': data['id']}
    update = {'$set': {'title': message.text}}
    tasks_collection.update_one(filter, update)
    await state.clear()
    await message.answer("Заголовок задачи изменен ")

@router.message(UpdateForm.note)
async def upd_note(message: Message, state: FSMContext):
    data = await state.get_data()
    filter = {'id': data['id']}
    update = {'$set': {'note': message.text}}
    tasks_collection.update_one(filter, update)
    await state.clear()
    await message.answer("Примечание задачи изменено")

@router.message(UpdateForm.time)
async def upd_time(message: Message, state: FSMContext):
    if await check_time(message.text):
        data = await state.get_data()
        filter = {'id': data['id']}
        update = {'$set': {'time': data['time']+ ' '+ message.text}}
        tasks_collection.update_one(filter, update)
        await state.clear()
        await message.answer("Время задачи изменено")
    else:
        await message.answer("Введен некорктный формат времени\n"
                             "Введите время в формате H:M")