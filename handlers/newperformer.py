from aiogram import Router,types
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup, InlineKeyboardButton,InlineKeyboardMarkup
from aiogram.types import Message
from aiogram.filters import Text
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from states.PerformForm import PerformForm
from DB.connect import db,performers_collection

router = Router()

async def check_fio(message):
    try:
        fio=message.split()
        if len(fio)==3:
            return True
        else:
            return False
    except:
        return False

@router.callback_query(Text(startswith= 'change_'))
async def callbacks_change(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.split('_')[1]
    if action == 'name':
        await callback.message.edit_text("Введите ФИО")
        await state.set_state(PerformForm.name)
    elif action =='id':
        await callback.message.edit_text("Введите ID")
        await state.set_state(PerformForm.change_id)
@router.callback_query(Text(startswith= 'data_'))
async def callbacks_data(callback: types.CallbackQuery, state: FSMContext):
    action = callback.data.split('_')[1]
    if action == 'true':
        data = await state.get_data()
        performer= {
            'id': data['id'],
            'FIO':data['name']
        }
        performers_collection.insert_one(performer)
        await callback.message.edit_text("Исполнитель добавлен")
        await state.clear()
    elif action == 'change':
        buttons=[
            [InlineKeyboardButton(text="Изменить ФИО", callback_data='change_name')],
            [InlineKeyboardButton(text="Изменить ID", callback_data='change_id')]
        ]
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)
        await callback.message.edit_text(text=callback.message.text)
        await callback.message.answer("Что хотите изменить", reply_markup=markup)

@router.callback_query(Text(startswith= 'performer_'))
async def callbacks_performers(callback: types.CallbackQuery, state: FSMContext):
    performer = callback.data.split('_')[1]
    if performer == 'self':
        performers = performers_collection.find_one({'id': callback.from_user.id})
        if performers:
            await callback.message.edit_text("Вы уже являетесь исполнителем")
            await state.clear()
        else:
            await state.set_state(PerformForm.name)
            await state.update_data(id=callback.from_user.id)
            await callback.message.edit_text("Введи свое ФИО")
    elif performer == 'other':
        await state.set_state(PerformForm.id)
        await callback.message.edit_text("Введи ID пользователя")

@router.message(Command("add_performer"))
async def cmd_add_performer(message: Message, state: FSMContext):
    button = [
        [KeyboardButton(text='Назад')]
    ]
    markup = ReplyKeyboardMarkup(keyboard=button, resize_keyboard=True)
    await message.answer("Новый исполнитель задачи",reply_markup=markup)
    await message.delete()
    buttons = [
        [InlineKeyboardButton(text = "Исполнитель я",callback_data = 'performer_self')],
        [InlineKeyboardButton(text = "Исполнитель другой человек",callback_data = 'performer_other')]
    ]
    markup = InlineKeyboardMarkup(inline_keyboard = buttons)
    await state.set_state(PerformForm.start)
    await message.answer("Кто будет исполнителем? ",reply_markup=markup)


@router.message(PerformForm.id)
async def process_id(message: Message, state: FSMContext):
    if message.text.isdigit():
        performers = performers_collection.find_one({'id': int(message.text)})
        if performers:
            await message.answer("Человек уже является исполнителем")
            await state.clear()
        else:
            await state.update_data(id=int(message.text))
            await state.set_state(PerformForm.name)
            await message.answer("Введи ФИО исполнителя")
    else:
        await message.answer("ID должно быть численным значением")
        await state.set_state(PerformForm.id)
        await message.answer("Введи ID пользователя")


@router.message(PerformForm.name)
async def process_name(message: Message, state: FSMContext):
    if await check_fio(message.text):
        await state.update_data(name = message.text)
        data = await state.get_data()
        buttons = [
            [InlineKeyboardButton(text="Да, все верно", callback_data='data_true')],
            [InlineKeyboardButton(text="Нет,хочу отредактировать", callback_data='data_change')]
        ]
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)
        await message.answer(f'Проверьте корректность данных:\n'
                             f'ID - {data["id"]}\n'
                             f'ФИО исполнителя - {data["name"]}\n', reply_markup=markup)
    else:
        await message.answer("Не все данные введены\n"
                             "Введите ФИО еще раз\n"
                             "Пример: Петров Петр Петрович")

@router.message(PerformForm.change_id)
async def change_id(message: Message, state: FSMContext):
    if message.text.isdigit():
        await state.update_data(id=int(message.text))
        data = await state.get_data()
        buttons = [
            [InlineKeyboardButton(text="Да, все верно", callback_data='data_true')],
            [InlineKeyboardButton(text="Нет,хочу отредактировать", callback_data='data_change')]
        ]
        markup = InlineKeyboardMarkup(inline_keyboard=buttons)
        await message.answer(f'Проверьте корректность данных:\n'
                             f'ID - {data["id"]}\n'
                             f'ФИО исполнителя - {data["name"]}\n', reply_markup=markup)
    else:
        await message.answer("ID должно быть численным значением")
        await state.set_state(PerformForm.change_id)
        await message.answer("Введи ID пользователя")