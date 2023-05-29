from aiogram import Router,types
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton,InlineKeyboardMarkup
from aiogram.types import Message
from aiogram.filters import Text
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from states.DeleteForm import DeleteForm
from DB.connect import tasks_collection

router = Router()


@router.callback_query(Text(startswith= 'delete_'))
async def callbacks_delete(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.split('_')[1]
    if action == 'yes':
        data = await state.get_data()
        filter = {'id': data['id']}
        result = tasks_collection.delete_one(filter)
        if result.deleted_count == 1:
            await callback.message.edit_text("Запись успешно удалена")
        else:
            await callback.message.edit_text("Запись не найдена")
        await state.clear()
    else:
        await callback.message.edit_text("Запись не удалена")
        await state.clear()

@router.message(Command("delete_task"))
async def cmd_tasks(message: Message, state: FSMContext):
    button = [
        [KeyboardButton(text='Назад')]
    ]
    markup = ReplyKeyboardMarkup(keyboard=button, resize_keyboard=True)
    await message.answer("Введи ID задачи которую нужно удалить",reply_markup=markup)
    await state.set_state(DeleteForm.id)


@router.message(DeleteForm.id)
async def delete_task(message: Message, state: FSMContext):
    if message.text.isdigit():
        id = int(message.text)
        await state.update_data(id=id)
        try:
            task = tasks_collection.find_one({'id': id})
            response = "Вы действительно хотите удалить эту задачу?\n" \
                       f"Задача: {task['title']}\n" \
                       f"Время: {task['time']}\n" \
                       f"Исполнитель: {task['assignee']}\n" \
                       f"Примечание: {task['note']}\n" \
                       f"Статус: {task['status']}\n"
            buttons = [
                [InlineKeyboardButton(text="Да", callback_data='delete_yes')],
                [InlineKeyboardButton(text="Нет", callback_data='delete_no')]
            ]
            markup = InlineKeyboardMarkup(inline_keyboard=buttons)
            await message.answer(response, reply_markup=markup)
        except:
            await message.answer("Задачи по такому ID нет")
    else:
        await message.answer("ID должно быть численным значением")