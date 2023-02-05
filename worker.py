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
from datetime import datetime

import service


start_message = 'Привет! Бот для фиксирования времени выполнения задач джира'
help = 'Комманды:\n\n\
      /enter_new_task - ввести новую задачу\n\
      /out_all_active_tasks - вывод всех активных задач\n\
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

# States Enter Task
class FormEnterTask (StatesGroup):
    TASK_ID = State()    
    DESCRIBE = State()

# States Enter Time Task
class FormEnterTime (StatesGroup):
    TASK_ID = State()

    
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# Create the client
client = pymongo.MongoClient('localhost', 27017)
database = client['TASK_MANAGER_DB']


@dp.message_handler(commands=['start'])
async def start_handler(message: types.Message):
    print(f'{message.from_user.id} {message.from_user.full_name} {time.asctime()}')
    await message.reply(MESSAGES['help'])

@dp.message_handler(commands=['enter_time'])
async def process_enter_time_command(message: types.Message,state: FSMContext):
    await FormEnterTime.TASK_ID.set()
    await message.reply('Введите ID задачи = ')

#Обработка ввода времени джира
@dp.message_handler(state=FormEnterTime.TASK_ID)
async def process_TIME_TASK(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['TASK_ID'] = message.text
        
    datestr = str(datetime.now())[0:19]
    print('data[TASK_ID]: ' + data['TASK_ID'])

    database['TASK_LIST'].update_one({ 'TASK_ID': data['TASK_ID']},
                                  {'$push': { "TIME_ARRAY":  datetime.strptime(datestr, "%Y-%m-%d %H:%M:%S")}}) 


    all_task_time = 0.0
    all_task_time = service.calculate_value_in_TIME_ARRAY(data['TASK_ID'])

    await bot.send_message(message.from_user.id,'Всего часов затрачено на задачу ('+ data['TASK_ID']+'): ' +  str(all_task_time/60/60))
    await state.finish()

@dp.message_handler(commands='enter_new_task')
async def enter_new_task_process(message: types.Message):
    await FormEnterTask.TASK_ID.set()
    await message.reply("Введите TASK_ID:")


#Обработка ввода ID задачи из джира
@dp.message_handler(state=FormEnterTask.TASK_ID)
async def process_TASK_ID(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['TASK_ID'] = message.text

    await FormEnterTask.next()
    await message.reply("Введите описание задачи:")
    


@dp.message_handler(state=FormEnterTask.DESCRIBE)
async def process_DESCRIBE(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['DESCRIBE'] = message.text

        await bot.send_message(
            message.chat.id,
            md.text(
                md.text('TASK_ID,', md.bold(data['TASK_ID'])),
                md.text('DESCRIBE:', md.code(data['DESCRIBE'])),
                sep='\n'
            )
        )

        datestr = str(datetime.now())[0:19]
        print("datestr: " + datestr)
        
        obj = { 
                'TASK_ID':  data['TASK_ID'],
                'DESCRIBE': data['DESCRIBE'],
                'TIME_ARRAY': [datetime.strptime(datestr, "%Y-%m-%d %H:%M:%S")]
              }

        database['TASK_LIST'].insert_one(obj)

    await state.finish()

@dp.message_handler(commands=['out_all_active_tasks'])
async def process_out_active_tasks_command(message: types.Message):
    
    textMessage = ''
    result = database['TASK_LIST'].find({
        'TIME_ARRAY': [0]})
    
    buf_cursor = result.clone()

    list_result = list(buf_cursor)
    print(list_result)
    
    counter = 0
    for _item in list_result:
        textMessage = textMessage +"\n"+ _item['TASK_ID']+ "  :  " + str(_item['DESCRIBE'])
        counter = counter + 1

    await message.reply('В работе на данный момент находяться следущие задачи: \n' + textMessage + '\n\n Всего: ' + str(counter))

@dp.message_handler(commands=['help'])
async def process_help_command(message: types.Message):
    await message.reply(MESSAGES['help'])

if __name__ == "__main__":
    executor.start_polling(dp)
    
