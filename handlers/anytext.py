from aiogram import Router
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove

router = Router()


@router.message()
async def anytext(message: Message):
    await message.answer("Я тебя не понимаю. Выбери одну из команд в меню для начала работы")