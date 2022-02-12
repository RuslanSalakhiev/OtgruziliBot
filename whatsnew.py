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
from keyboards.kb_whatsnew import show_book_keyboard, select_period_keyboard, select_publisher_keyboard, book_mode_keyboard


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
    select_book_mode = State()
    show_list_book = State()
    show_single_book = State()

async def delete_message(message: types.Message):
    await message.delete()


async def select_period(call: types.CallbackQuery):
    await delete_message(call.message)
    await Whatsnew.select_period.set()
    await call.message.answer('За какой период посмотрим новинки?', reply_markup = select_period_keyboard())
    await call.answer()

async def select_publisher(call: types.CallbackQuery, state: FSMContext, days):
    await delete_message(call.message)
    await Whatsnew.select_publisher.set()
    async with state.proxy() as data:
        from_date = dt.datetime.now() - dt.timedelta(days=7)

        # Сбор статистики по новинкам по издательствам
        publisher_stats = [{'name': p['name'], 'newbooks': len(find_books(config.db_name, publisher_id=p['id'], from_date=from_date))} for p in get_all_publishers(config.db_name)]

    await call.message.answer('Новинки какого издательства посмотрим?', reply_markup = select_publisher_keyboard(publishers=publisher_stats))
    await call.answer()


# async def process_correct_publisher(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['publisher'] = find_publisher(config.db_name, message.text)
#         from_date = dt.datetime.now() - dt.timedelta(days=data['period'])
#         data['books'] = find_books(config.db_name, publisher_id=data['publisher']['id'], from_date=from_date)
#         data['count_books'] = len(data['books'])
#         data['book_counter'] = 0
#
#     await message.reply(f" В {data['publisher']['name']} за {data['period']} дней вышло {data['count_books']} книг\n \
#                         Давай их посмотрим?", reply_markup=show_book_keyboard())
#     countr[message.from_user.id] = data['count_books'] - 1
#     await Whatsnew.next()


async def book_mode(call: types.CallbackQuery):
    await delete_message(call.message)
    await Whatsnew.select_book_mode.set()
    await call.message.answer('Как показать книги?', reply_markup = book_mode_keyboard())
    await call.answer()

async def show_book(message: types.Message, book):
    await delete_message(call.message)
    await message.answer(book_preview(book), parse_mode="HTML", reply_markup=show_book_keyboard())

def book_preview(book):
    return f'''
<b>{book['title']}</b>
{book['author']}
---    
{book['short_abstract']}   
'''

# async def process_invalid_time(message: types.Message):
#     await message.answer('Неправильный период ¯\\_(ツ)_/¯. Либо 7, либо 30')
#
#
# async def process_correct_period(message: types.Message, state: FSMContext):
#     async with state.proxy() as data:
#         data['period'] = int(message.text)
#     await Whatsnew.next()
#
#     publisher_list = get_all_publishers(config.db_name)
#     all_publishers = []
#     for i in publisher_list:
#         all_publishers.append(i['name'])
#     all_publishers_str = ", ".join(all_publishers)
#     await message.reply(f"Теперь выбери издательство: {all_publishers_str}", reply_markup = select_publisher_keyboard())


# async def process_invalid_publisher(message: types.Message):
#     await message.answer('Неправильное издательство ¯\\_(ツ)_/¯')
#
#



async def counter(call: types.CallbackQuery, state: FSMContext):
    async with state.proxy() as state_data:
        books = state_data['books']

    if call.data == 'count_incr':
        countr[call.from_user.id] -= 1
        await show_book(call.message, books[countr[call.from_user.id]])
    elif call.data == 'count_decr':
        countr[call.from_user.id] += 1
        await show_book(call.message, books[countr[call.from_user.id]])
    await call.answer()

