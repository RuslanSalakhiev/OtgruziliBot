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
import data
import whatsnew

# log_file = os.path.join(config.log_dir, "bot.log")
# logging.basicConfig(level=logging.INFO, filename=log_file)
logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
bot = Bot(token=config.token, parse_mode= types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)


# States
class Root(StatesGroup):
    main = State('main')  # The main dialog
    # /Whatsnew chain:
    # main -> /Whatsnew -> news -> Неделя/Месяц -> publisher -> МИФ/Альпина ->
    # -> book_preview -> По одной/Все -> show_mode
    news = State('news')  # Appears after \Whatsnews command
    publisher = State('publisher')  # Chose publisher after chosing time period

    # main -> /Unsubscribe -> unsubscribe_publishers -> МИФ/Альпина -> main


class Subscribe(StatesGroup):
    # /Subscribe chain:
    # main -> /Subscribe -> subscribe_publishers -> МИФ/Альпина ->
    # -> subscribe_perido -> Месяц/неделя -> main
    publishers = State('subscribe_publishers')
    period = State('subscribe_period')
    current_publisher = None


dp.register_message_handler(whatsnew.select_period,
                            commands=['Whatsnew'],
                            state='*')

dp.register_message_handler(whatsnew.process_invalid_time,
                            lambda message: message.text not in {'7', '30'},
                            state=whatsnew.Whatsnew.select_period)

dp.register_message_handler(whatsnew.process_correct_period,
                            state=whatsnew.Whatsnew.select_period)

dp.register_message_handler(whatsnew.process_invalid_publisher,
                            lambda message: message.text not in {'МИФ', 'Альпина', 'Corpus', 'Бумкнига'},
                            state=whatsnew.Whatsnew.select_publisher)

dp.register_message_handler(whatsnew.process_correct_publisher,
                            state=whatsnew.Whatsnew.select_publisher)

dp.register_callback_query_handler(whatsnew.counter, Text(startswith="count_"),
                                   state=whatsnew.Whatsnew.select_next_book)

def send_to_channel(text: str):
    executor.start(dp, main(text))


async def main(text: str):
    await send_message(config.chat_id, text)


async def send_message(channel_id: int, text: str):
    await bot.send_message(channel_id, text)


@dp.message_handler(commands=['Start'], state='*')
async def process_start(message: types.Message):
    await Root.main.set()
    await message.answer('Привет, это бот книжных новинок. \
    Подпишись на новинки любимого издательства или посмотри какие книги недавно поступили в продажу')


@dp.message_handler(commands=['Help'], state='*')
async def process_help(message: types.Message):
    await Root.main.set()
    await message.answer('''Вот список команд:
                         /Whatsnew - получить список новинок
                         /Subscribe - подписаться на издательство
                         /Unsubscribe - отписаться от издательства
                         /help - инструкция по работе с ботом''')


# @dp.message_handler(commands=['Whatsnew'], state='*')
async def process_whatsnew(message: types.Message):
    # Configure ReplyKeyboardMarkup
    # print(f"Current state: {dp.get_current().current_state()}")
    await Root.news.set()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("Неделя", "Месяц")
    await message.answer('За какой период показать новинки?',
                         reply_markup=markup)


# @dp.message_handler(lambda message: message.text not in {'Неделя', 'Месяц'}, state=Root.news)
async def process_invalid_time(message: types.Message):
    await message.answer('Не правильный период.')


@dp.message_handler(commands=['subscribe'])
async def process_subscribe(message: types.Message):
    publishers = data.get_all_publishers(config.db_name)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    for p in publishers:
        markup.add(p['name'])
    await Subscribe.publishers.set()
    await message.answer('На какое издательство подписаться?',
                         reply_markup=markup)


@dp.message_handler(state=Subscribe.publishers)
async def process_subscribe_publishers(message: types.Message):
    publishers = [p['name'] for p in data.get_all_publishers(config.db_name)]
    if message.text in publishers:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add("Раз в месяц", "Раз в неделю")
        Subscribe.current_publisher = message.text
        await Subscribe.period.set()
        await message.answer("Как часто присылать уведомления?", reply_markup=markup)
    else:
        await message.answer('Такого издательства не существует')


@dp.message_handler(state=Subscribe.period)
async def process_subscribe_period(message: types.Message):
    if message.text.lower() in {"раз в месяц", "месяц"}:
        period = "0 10 1 * *"
    elif message.text.lower() in {"раз в неделю", "неделя"}:
        period = period = "0 10 * * 1"
    else:
        await message.answer('Выбран неверный период, допустимые значения: \
                             раз в месяц, раз в неделю')
        return
    # add subscription to database
    data.add_subscription(config.db_name, message.from_user.id, Subscribe.current_publisher, period)
    await Root.main.set()
    await message.answer(f"Вы, {message.from_user.username}, подписаны на издательство {Subscribe.current_publisher}",
                         reply_markup=types.ReplyKeyboardRemove())
    Subscribe.current_publisher = None


@dp.message_handler(commands=['logo'])
async def logo(message: types.Message):
    await message.answer_photo('https://res.cloudinary.com/dk-hub/images/q_70,c_limit,h_580,w_440,f_auto/dk-core-nonprod/9780241470992/9780241470992_cover.jpg/dk_Dinosaurs_and_Other_Prehistoric_Life')


@dp.message_handler()
async def echo(message: types.Message):
    await message.answer(message.text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
