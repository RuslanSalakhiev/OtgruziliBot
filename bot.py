import logging
import datetime as dt
import os.path
import asyncio

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup

# imports token, db_name
import config
import data
import subscribe
import whatsnew
from keyboards.kb_whatsnew import main_menu_keyboard,send_to_channel_keyboard

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


@dp.callback_query_handler(lambda call: call.data in ('navi_start','navi_main_menu'), state ='*')
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
                            lambda call: call.data in ('whatsnew','navi_whatsnew_period'),
                            state='*')

dp.register_callback_query_handler(whatsnew.select_publisher,
                            lambda call: call.data in ('7','30','navi_whatsnew_publishers'),
                            # lambda state:state._state in (whatsnew.Whatsnew.select_period,whatsnew.Whatsnew.select_book_mode)
                            state = '*')

dp.register_callback_query_handler(whatsnew.book_mode,
                            lambda call: call.data in ('1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','navi_whatsnew_book_mode'), #хардкод - убрать
                            # lambda state:state._state in (whatsnew.Whatsnew.select_publisher, whatsnew.Whatsnew.show_single_book, whatsnew.Whatsnew.show_list_book)
                            state = '*')

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

# отправка сообщений в технический канал
def send_to_channel(chat_id:int, message_type:str, text: str = None, photo_url:str = None, url:str =None, keyboard:bool = False):
    if message_type == 'text':
        executor.start(dp, send_message(chat_id,text))
    elif message_type == 'photo':
        file_id = executor.start(dp, send_photo(chat_id,photo_url, text,url,keyboard))
        return file_id

# получение file_id обложек
async def send_photo(channel_id: int, photo_url: str,text,url,keyboard):
    reply_markup = InlineKeyboardMarkup()
    if keyboard: reply_markup = send_to_channel_keyboard(url)
    response = await bot.send_photo(channel_id,photo=photo_url, caption=text, reply_markup=reply_markup)
    return response['photo'][0]['file_id']

async def send_message(channel_id: int, text: str):
    await bot.send_message(channel_id, text)


@dp.message_handler()
async def echo(message: types.Message):
    await message.answer(message.text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
