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
from data import get_all_publishers, find_books, find_publisher

# log_file = os.path.join(config.log_dir, "bot.log")
# logging.basicConfig(level=logging.INFO, filename=log_file)
logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
bot = Bot(token=config.token, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)

# Переменная для счетчика книг
countr = {}


# whatsnew states
class Whatsnew(StatesGroup):
    select_period = State()
    select_publisher = State()
    select_next_book = State()


##### Whatsnew #####
# @dp.message_handler(commands=['Whatsnew'], state=None)
async def select_period(message: types.Message):
    await Whatsnew.select_period.set()
    await message.answer('За какой период посмотрим новинки? \n \
                         Введи количество дней: 7 или 30')


# @dp.message_handler(lambda message: message.text not in {'7', '30'}, state=Whatsnew.select_period)
async def process_invalid_time(message: types.Message):
    await message.answer('Неправильный период ¯\\_(ツ)_/¯. Либо 7, либо 30')


# @dp.message_handler(state=Whatsnew.select_period)
async def process_correct_period(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['period'] = int(message.text)
    await Whatsnew.next()

    publisher_list = get_all_publishers(config.db_name)
    all_publishers = []
    for i in publisher_list:
        all_publishers.append(i['name'])
    all_publishers_str = ", ".join(all_publishers)
    await message.reply(f"Теперь выбери издательство: {all_publishers_str}")


async def process_invalid_publisher(message: types.Message):
    await message.answer('Неправильное издательство ¯\\_(ツ)_/¯')


async def process_correct_publisher(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['publisher'] = find_publisher(config.db_name, message.text)
        from_date = dt.datetime.now() - dt.timedelta(days=data['period'])
        data['books'] = find_books(config.db_name, publisher_id=data['publisher']['id'], from_date=from_date)
        data['count_books'] = len(data['books'])
        data['book_counter'] = 0

    await message.reply(f" В {data['publisher']['name']} за {data['period']} дней вышло {data['count_books']} книг\n \
                        Давай их посмотрим?", reply_markup=next_keyboard())
    countr[message.from_user.id] = data['count_books'] - 1
    await Whatsnew.next()


def book_preview(book):
    return f'''
        <b>{book['author']}</b>    
        {book['title']}
        {book['short_abstract']}  
        {book['url'] if book['url'] else ''}     
        '''


async def show_book(message: types.Message, book):
    await message.answer(book_preview(book), parse_mode="HTML", reply_markup=next_keyboard())


def next_keyboard():
    buttons = [
        types.InlineKeyboardButton(text="Дальше", callback_data="count_incr"),
        types.InlineKeyboardButton(text="Назад", callback_data="count_decr"),
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard


# @dp.callback_query_handler(Text(startswith="count_"), state = Whatsnew.select_next_book)
async def counter(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as state_data:
        books = state_data['books']

    if call.data == 'count_incr':
        countr[call.from_user.id] -= 1
        await show_book(call.message, books[countr[call.from_user.id]])
    elif call.data == 'count_decr':
        countr[call.from_user.id] += 1
        await show_book(call.message, books[countr[call.from_user.id]])
    # await call.answer()

# async def process_news_time(message: types.Message):
#    def books_info(books):
#        text = "\n".join([b['author'] + " " + b['title'] for b in books])
#        return text
#    markup = types.ReplyKeyboardRemove()
#    if message.text == 'Неделя':
#        from_date = dt.datetime.now() - dt.timedelta(days=7)
#    else:  # message.text == 'Месяц':
#        from_date = dt.datetime.now() - dt.timedelta(days=30)
#    to_date = dt.datetime.now()
#    book_text = books_info(find_books(config.db_name, from_date=from_date, to_date=to_date))
#    # await Root.main.set()
#    await message.answer(book_text, reply_markup=markup)
