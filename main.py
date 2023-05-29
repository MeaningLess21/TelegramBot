import logging
import config
import asyncio
import aiogram.enums.parse_mode
from aiogram import Bot, Dispatcher,Router
from aiogram.filters import Command, Text
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, ReplyKeyboardRemove
import handlers.deadlines as deadlines
from handlers.newtask import router as newtask_router
from handlers.alltasks  import router as alltasks_router
from handlers.newperformer  import router as newperformer_router
from handlers.common  import router as common_router
from handlers.updatetask  import router as update_router
from handlers.mytasks  import router as mytasks_router
from handlers.deletetask  import router as deltasks_router
from handlers.anytext  import router as anytext_router

# Устанавливаем уровень логов
logging.basicConfig(level=logging.INFO)
# Конфигурация бота
bot = Bot(token=config.bot_token, parse_mode= aiogram.enums.parse_mode.ParseMode.HTML)

router = Router()

@router.message(Command(commands=["back"]))
@router.message(Text(text="Назад", ignore_case=True))
async def cmd_cancel(message: Message, state: FSMContext):
    if not await state.get_state() == None:
        await state.clear()
        await bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
        await message.answer(
            text="Действие отменено",
            reply_markup=ReplyKeyboardRemove()
        )
    else:
        await message.answer(
            text="Действий нет",
            reply_markup=ReplyKeyboardRemove()
        )
async def main():
    dp = Dispatcher()
    dp.include_router(router)
    dp.include_router(common_router)
    dp.include_router(newtask_router)
    dp.include_router(alltasks_router)
    dp.include_router(newperformer_router)
    dp.include_router(update_router)
    dp.include_router(mytasks_router)
    dp.include_router(deltasks_router)
    dp.include_router(anytext_router)
    # loop = asyncio.get_event_loop()
    # loop.create_task(deadlines.check_new_tasks())
    asyncio.ensure_future(deadlines.check_task_deadlines())
    asyncio.ensure_future(deadlines.check_new_tasks())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
