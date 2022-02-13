import logging
import datetime as dt
import os.path
import asyncio

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text

# imports token, db_name
import config
import data
import subscribe
import whatsnew
from keyboards.kb_whatsnew import main_menu_keyboard

# log_file = os.path.join(config.log_dir, "bot.log")
# logging.basicConfig(level=logging.INFO, filename=log_file)
logging.basicConfig(level=logging.INFO)
storage = MemoryStorage()
bot = Bot(token=config.token, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)


# States
class Root(StatesGroup):
    main = State('main')  # The main dialog


@dp.message_handler(commands=['Start'], state='*')
async def process_start(message: types.Message):
    await Root.main.set()
    await message.answer('Привет, это бот книжных новинок. \
    Подпишись на новинки любимого издательства или посмотри какие книги недавно поступили в продажу', reply_markup = main_menu_keyboard())


@dp.callback_query_handler(text = 'navi_start', state ='*')
async def process_start(call: types.CallbackQuery):
    await Root.main.set()
    await whatsnew.delete_message(call.message)
    await call.message.answer('Привет, это бот книжных новинок. \
    Подпишись на новинки любимого издательства или посмотри какие книги недавно поступили в продажу', reply_markup = main_menu_keyboard())
    await call.answer()

@dp.message_handler(commands=['Help'], state='*')
async def process_help(message: types.Message):
    await Root.main.set()
    await message.answer('''Вот список команд:
                         /Whatsnew - получить список новинок
                         /Subscribe - подписаться на издательство
                         /Unsubscribe - отписаться от издательства
                         /help - инструкция по работе с ботом''')

dp.register_callback_query_handler(whatsnew.select_period,
                            text='whatsnew',
                            state='*')

dp.register_callback_query_handler(whatsnew.select_publisher,
                            lambda call: call.data in ('7','30'),
                            state=whatsnew.Whatsnew.select_period)

dp.register_callback_query_handler(whatsnew.book_mode,
                            lambda call: call.data in ('1','2','3','4'), #хардкод - убрать
                            state=whatsnew.Whatsnew.select_publisher)

dp.register_callback_query_handler(whatsnew.show_list_book,
                            text='list',
                            state=whatsnew.Whatsnew.select_book_mode)


dp.register_callback_query_handler(whatsnew.show_single_book,
                            Text(startswith="count_"),
                            state=whatsnew.Whatsnew.select_book_mode)


# Handlers for /subscribe
dp.register_message_handler(subscribe.start_subscribe, commands=['Subscribe'])

dp.register_message_handler(subscribe.process_publisher,
                            state=subscribe.BranchStates.select_publisher)

dp.register_message_handler(subscribe.process_period,
                            state=subscribe.BranchStates.select_period)



def send_to_channel(text: str):
    executor.start(dp, main(text))


async def main(text: str):
    await send_message(config.chat_id, text)


async def send_message(channel_id: int, text: str):
    await bot.send_message(channel_id, text)


@dp.message_handler()
async def echo(message: types.Message):
    await message.answer(message.text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
