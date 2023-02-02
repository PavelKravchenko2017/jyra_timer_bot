import pymongo
import time
import logging
import asyncio
from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters.state import State, StatesGroup
import aiogram.utils.markdown as md
from aiogram.types import ParseMode

from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext

global current_ID_TASK
current_ID_TASK = ''

start_message = 'Привет! Бот для фиксирования времени выполнения задач'
help = 'Комманды:\n\n \
      /enter_new_task - ввести новую задачу \n \
      /out_all_active_tasks - вывод всех активных задач \n  \
      /enter_time - ввести значение времени задачи'

start_couting = 'start_couting'
TOKEN = "5904213471:AAGvgOuEZ8E0wP_ZcoTV8yyZG1T06GUJIYA"

bot = Bot(token=TOKEN)
dp = Dispatcher(bot=bot)

MESSAGES = {
    'start': start_message,
    'help': help,
    'start_couting': start_couting
}

# States
class FormEnterTask (StatesGroup):
    ID_TASK = State()    
    DESCRIBE = State()

storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# Create the client
client = pymongo.MongoClient('localhost', 27017)
db = client['TimerDB']
setter_collection = db['setter']

@dp.message_handler(commands=['enter_new_tasks'])
async def process_help_command(message: types.Message):
    await message.reply('Введите ID задачи = ')

@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):

    print(f'{message.from_user.id} {message.from_user.full_name} {time.asctime()}')
    
    await message.reply(MESSAGES['help'])


@dp.message_handler(commands='enter_new_task')
async def enter_new_task_process(message: types.Message):
   
    await FormEnterTask.ID_TASK.set()
    await message.reply("Введите ID_TASK:")


#Обработка ввода ID задачи из джира
@dp.message_handler(state=FormEnterTask.ID_TASK)
async def process_ID_TASK(message: types.Message, state: FSMContext):
    
    async with state.proxy() as data:
        data['ID_TASK'] = message.text
        
    await FormEnterTask.next()
    await message.reply("Введите описание задачи:")



@dp.message_handler(state=FormEnterTask.DESCRIBE)
async def process_DESCRIBE(message: types.Message, state: FSMContext):
    print("process_DESCRIBE_1")
    async with state.proxy() as data:
        data['DESCRIBE'] = message.text

        # Remove keyboard
        #markup = types.ReplyKeyboardRemove()

        # And send message
        await bot.send_message(
            message.chat.id,
            md.text(
                md.text('TASK_ID,', md.bold(data['ID_TASK'])),
                md.text('DESCRIBE:', md.code(data['DESCRIBE'])),
                sep='\n'
            )
        )

    # Finish conversation
    await state.finish()


@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply(MESSAGES['start_couting'])





# @dp.message_handler()
# async def echo_message(msg: types.Message):
#     await bot.send_message(msg.from_user.id,'Блядская давалка')


if __name__ == "__main__":
    executor.start_polling(dp)
    
