from aiogram import Router
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
router = Router()

@router.message(Command(commands=["start"]))
@router.message(Text(text="старт", ignore_case=True))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text= f"Приветсвую, {message.from_user.first_name}!\n"
                               f"Для начала работы выберите одну из команд в меню")

