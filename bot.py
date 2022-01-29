import logging
import datetime as dt
import os.path

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

# imports token, db_name
import config
import data

# log_file = os.path.join(config.log_dir, "bot.log")
# logging.basicConfig(level=logging.INFO, filename=log_file)
logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
bot = Bot(token=config.token)
dp = Dispatcher(bot, storage=storage)


# States
class Dialog(StatesGroup):
    main = State('main')  # The main dialog
    news = State('news')  # Appears after \Whatsnews command


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


@dp.message_handler(commands=['Whatsnew'], state='*')
async def process_whatsnew(message: types.Message):
    # Configure ReplyKeyboardMarkup
    # print(f"Current state: {dp.get_current().current_state()}")
    await Dialog.news.set()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("Неделя", "Месяц")
    await message.answer('За какой период показать новинки?',
                         reply_markup=markup)


@dp.message_handler(lambda message: message.text not in {'Неделя', 'Месяц'}, state=Dialog.news)
async def process_invalid_time(message: types.Message):
    await message.answer('Не правильный период.')


@dp.message_handler(lambda message: message.text in {'Неделя', 'Месяц'}, state=Dialog.news)
async def process_news_time(message: types.Message):
    def books_info(books):
        text = "\n".join([b['author'] + " " + b['title'] for b in books])
        return text
    markup = types.ReplyKeyboardRemove()
    if message.text == 'Неделя':
        from_date = dt.datetime.now() - dt.timedelta(days=7)
    else:  # message.text == 'Месяц':
        from_date = dt.datetime.now() - dt.timedelta(days=30)
    to_date = dt.datetime.now()
    book_text = books_info(data.find_books(config.db_name, from_date=from_date, to_date=to_date))
    await Dialog.main.set()
    await message.answer(book_text, reply_markup=markup)


@dp.message_handler(commands=['subscribe'])
async def process_subscribe(message: types.Message):
    publishers = data.get_all_publishers(config.db_name)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    for p in publishers:
        markup.add(p['name'])
    await message.answer('На какое издательство подписаться?',
                         reply_markup=markup)


@dp.message_handler(commands=['logo'])
async def logo(message: types.Message):
    await message.answer_photo('https://res.cloudinary.com/dk-hub/images/q_70,c_limit,h_580,w_440,f_auto/dk-core-nonprod/9780241470992/9780241470992_cover.jpg/dk_Dinosaurs_and_Other_Prehistoric_Life')


@dp.message_handler()
async def echo(message: types.Message):
    await message.answer(message.text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
