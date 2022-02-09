import logging
import datetime as dt
import os.path

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text

# imports token, db_name
import config
from data import get_all_publishers, find_books
# log_file = os.path.join(config.log_dir, "bot.log")
# logging.basicConfig(level=logging.INFO, filename=log_file)
logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
bot = Bot(token=config.token, parse_mode= types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)

# Переменная для счетчика книг
countr = {}

# whatsnew states
class Whatsnew(StatesGroup):
    select_period = State()
    select_publisher = State()
    select_next_book = State()


##### Whatsnew #####
@dp.message_handler(commands=['Whatsnew'], state=None)
async def start(message: types.Message):
	await Whatsnew.select_period.set()
	await message.reply('За какой период посмотрим новинки?')

@dp.message_handler(lambda message: message.text not in {'7', '30'}, state=Whatsnew.select_period)
async def process_invalid_time(message: types.Message):
    await message.answer('Неправильный период ¯\_(ツ)_/¯. Либо 7, либо 30')

@dp.message_handler(state=Whatsnew.select_period)
async def period(message: types.Message, state:FSMContext):
    async with state.proxy() as data:
        data['period'] = message.text
    await Whatsnew.next()

    publisher_list = [{'name': p['name'], 'publisher_id': p['publisher_id']} for p in get_all_publishers(config.db_name)]
    all_publishers = []
    for i in publisher_list:
        all_publishers.append(i['name'])
    all_publishers_str = ", ".join(all_publishers)
    await message.reply(f"Теперь выбери издательство: {all_publishers_str}")

@dp.message_handler(lambda message: message.text not in {'МИФ', 'Альпина', 'Corpus', 'Бумкнига'}, state=Whatsnew.select_publisher)
async def process_invalid_time(message: types.Message):
    await message.answer('Неправильное издательство ¯\_(ツ)_/¯')

@dp.message_handler(state=Whatsnew.select_publisher)
async def publisher(message: types.Message, state:FSMContext):
    async with state.proxy() as data:
        data['publisher'] = message.text
        data['count_books'] = len(find_books(config.db_name, publisher_id='1', from_date= '2022-01-03'))
        data['book_counter'] = 0

    await message.reply(f" В {data['publisher']} за {data['period']} дней вышло {data['count_books']} книг\n Давай их посмотрим?", reply_markup=next_keyboard())
    countr[message.from_user.id] = data['count_books']-1

    await Whatsnew.next()

async def show_book(message: types.Message, book_value: int):
    await message.reply(f'''
    {find_books(config.db_name, publisher_id='1',from_date='2022-02-03')[book_value][2]}    
    {find_books(config.db_name, publisher_id='1',from_date='2022-02-03')[book_value][7]} 
    {find_books(config.db_name, publisher_id='1',from_date='2022-02-03')[book_value][8]} 
    {find_books(config.db_name, publisher_id='1',from_date='2022-02-03')[book_value][5]} 
    ''', reply_markup=next_keyboard())

def next_keyboard():
    buttons = [
        types.InlineKeyboardButton(text="Дальше", callback_data="count_incr"),
        types.InlineKeyboardButton(text="Назад", callback_data="count_decr"),
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard

@dp.callback_query_handler(Text(startswith="count_"), state = '*') #поправить на конкретный стейт
async def counter(call: types.CallbackQuery):
    if call.data == 'count_incr':
        countr[call.from_user.id]-=1
        await show_book(call.message, countr[call.from_user.id])
    elif call.data == 'count_decr':
        countr[call.from_user.id]+=1
        await show_book(call.message, countr[call.from_user.id])
    await call.answer()


#### Статистика в канал ######
def send_to_channel(text:str):
    executor.start(dp, main(text))

async def main(text:str):
    await send_message(config.chat_id, text)

async def send_message(channel_id: int, text: str):
    await bot.send_message(channel_id, text)

#### Общие хэндлеры ######

@dp.message_handler(commands=['Start'], state='*')
async def process_start(message: types.Message):
    await Dialog.main.set()
    await message.answer('Привет, это бот книжных новинок. \
    Подпишись на новинки любимого издательства или посмотри какие книги недавно поступили в продажу')


@dp.message_handler(commands=['Help'], state='*')
async def process_help(message: types.Message):
    await Dialog.main.set()
    await message.answer('''Вот список команд:
                         /Whatsnew - получить список новинок
                         /Subscribe - подписаться на издательство
                         /Unsubscribe - отписаться от издательства
                         /help - инструкция по работе с ботом''')

#### Subscribe ######

@dp.message_handler(commands=['subscribe'])
async def process_subscribe(message: types.Message):
    publishers = data.get_all_publishers(config.db_name)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    for p in publishers:
        markup.add(p['name'])
    await message.answer('На какое издательство подписаться?',
                         reply_markup=markup)

#### Echo

@dp.message_handler()
async def echo(message: types.Message):
    await message.answer(message.text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
