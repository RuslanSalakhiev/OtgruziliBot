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
from keyboards.kb_whatsnew import show_book_keyboard, select_period_keyboard, select_publisher_keyboard, book_mode_keyboard, show_list_keyboard


# log_file = os.path.join(config.log_dir, "bot.log")
# logging.basicConfig(level=logging.INFO, filename=log_file)
logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
bot = Bot(token=config.token, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)

# Переменная для счетчика книг
whatsnew_period = {}
whatsnew_publisher = {}
whatsnew_counter = {}
books_to_show = {}

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
    await call.message.answer('За какой период посмотрим новинки?', reply_markup = select_period_keyboard(previous_step='main_menu'))
    await call.answer()

async def select_publisher(call: types.CallbackQuery):
    await delete_message(call.message)

    # если колбэк не навигационный, то присвоить ид выбранного издательство
    if call.data != 'navi_whatsnew_publishers':
        whatsnew_period[call.from_user.id] = int(call.data)

    await Whatsnew.select_publisher.set()

    from_date = dt.datetime.now() - dt.timedelta(days=whatsnew_period[call.from_user.id])
    # Сбор статистики по новинкам по издательствам
    publisher_stats = [{'name': p['name'],'id': p['id'], 'newbooks': len(find_books(config.db_name, publisher_id=p['id'], from_date=from_date))} for p in get_all_publishers(config.db_name)]

    await call.message.answer('Новинки какого издательства посмотрим?', reply_markup = select_publisher_keyboard(publishers=publisher_stats,previous_step='whatsnew_period'))
    await call.answer()


async def book_mode(call: types.CallbackQuery):
    await delete_message(call.message)
    #проверка на навигационный колбэк
    if call.data != 'navi_whatsnew_book_mode':
        whatsnew_publisher[call.from_user.id] = call.data

    await Whatsnew.select_book_mode.set()
    await call.message.answer(f'Как показать книги?', reply_markup = book_mode_keyboard(previous_step='whatsnew_publishers'))

    # получение списка книг для выдачи
    from_date = dt.datetime.now() - dt.timedelta(days=whatsnew_period[call.from_user.id])
    books_to_show[call.from_user.id] = find_books(config.db_name, publisher_id=whatsnew_publisher[call.from_user.id], from_date=from_date)

    # начало отсчета книга
    whatsnew_counter[call.from_user.id] = 0
    await call.answer()

async def show_list_book(call: types.CallbackQuery):
    await delete_message(call.message)

    await call.message.answer(f'Список книг',reply_markup =show_list_keyboard(books=books_to_show[call.from_user.id], previous_step='whatsnew_publishers'))
    await call.answer()


async def show_single_book(call: types.CallbackQuery):
    await delete_message(call.message)
    if call.data == 'count_incr':
        # зациклить показ книг
        if whatsnew_counter[call.from_user.id] == len(books_to_show[call.from_user.id]) :
            whatsnew_counter[call.from_user.id] = 1
        else:
            whatsnew_counter[call.from_user.id] += 1
    elif call.data == 'count_decr':
        # зациклить показ книг
        if whatsnew_counter[call.from_user.id] == 1:
            whatsnew_counter[call.from_user.id] = len( books_to_show[call.from_user.id])
        else:
            whatsnew_counter[call.from_user.id] -= 1
    else:  #если коллбэк приходит из меню списков
        whatsnew_counter[call.from_user.id]=int(call.data.split('_')[1])

    await show_book(call.message, books_to_show[call.from_user.id][whatsnew_counter[call.from_user.id] - 1],whatsnew_counter[call.from_user.id], len(books_to_show[call.from_user.id]))
    await call.answer()


async def show_book(message: types.Message, book_value, counter, total_books):
    await message.answer_photo(caption = f'''
<i>[{counter}/{total_books}]</i> <b>{book_value['title']}</b>    
{book_value['author']} 
---
{book_value['short_abstract'][:600]}   
''', reply_markup=show_book_keyboard(book_value['url'],previous_step='whatsnew_book_mode'), photo = book_value['image_path'])



