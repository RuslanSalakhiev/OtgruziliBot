import logging

from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

# imports token, db_name
import config
import data

logging.basicConfig(level=logging.INFO)

storage = MemoryStorage()
bot = Bot(token=config.token, parse_mode= types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)


# States
class Dialog(StatesGroup):
    main = State('main')  # The main dialog
    news = State('news')  # Appears after \Whatsnews command

def send_to_channel(text:str):
    executor.start(dp, main(text))

async def main(text:str):
    await send_message(config.chat_id, text)

async def send_message(channel_id: int, text: str):
    await bot.send_message(channel_id, text)

@dp.message_handler(commands=['Start'], state='*')
async def process_start(message: types.Message):
    await Dialog.main.set()
    await message.answer('Привет, это бот книжных новинок. \
    Подпишись на новинки любимого издательства или посмотри какие книги недавно поступили в продажу')


@dp.message_handler(commands=['Help'], state='*')
async def process_help(message: types.Message):
    await message.answer('''Вот список команд:
                         /Whatsnew - получить список новинок
                         /Subscribe - подписаться на издательство
                         /Unsubscribe - отписаться от издательства
                         /help - инструкция по работе с ботом''')


@dp.message_handler(commands=['Whatsnew'], state=Dialog.main)
async def process_whatsnew(message: types.Message):
    # Configure ReplyKeyboardMarkup
    # print(f"Current state: {dp.get_current().current_state()}")
    await Dialog.news.set()
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    markup.add("Неделя", "Месяц")
    await message.answer('За какой период показать новинки?',
                         reply_markup=markup)


@dp.message_handler(lambda message: message.text in {'Неделя', 'Месяц'}, state=Dialog.news)
async def process_news_time(message: types.Message, state: FSMContext):
    markup = types.ReplyKeyboardRemove()
    # print(f"Current state: {dp.get_current().current_state()}")
    if message.text == 'Неделя':
        await Dialog.main.set()
        await message.answer('Новинки за неделю', reply_markup=markup)
    elif message.text == 'Месяц':
        await Dialog.main.set()
        await message.answer('Новинки за месяц', reply_markup=markup)
    else:
        await message.answer('Не правильный период.', reply_markup=markup)


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
