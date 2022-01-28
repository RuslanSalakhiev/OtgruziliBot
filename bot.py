import logging

from aiogram import Bot, Dispatcher, executor, types

import config

logging.basicConfig(level=logging.INFO)

bot = Bot(token=config.token)
dp = Dispatcher(bot)


@dp.message_handler(commands=['Start'])
async def process_start(message: types.Message):
    await message.answer('Привет, это бот книжных новинок. \
    Подпишись на новинки любимого издательства или посмотри какие книги недавно поступили в продажу')


@dp.message_handler(commands=['Help'])
async def process_help(message: types.Message):
    await message.answer('''Вот список команд:
                         /Whatsnew - получить список новинок
                         /Subscribe - подписаться на издательство
                         /Unsubscribe - отписаться от издательства
                         /help - инструкция по работе с ботом''')


@dp.message_handler(commands=['Whatsnew'])
async def process_whatsnew(message: types.Message):
    await message.answer('За какой период показать новинки?')


@dp.message_handler(commands=['logo'])
async def logo(message: types.Message):
    await message.answer_photo('https://res.cloudinary.com/dk-hub/images/q_70,c_limit,h_580,w_440,f_auto/dk-core-nonprod/9780241470992/9780241470992_cover.jpg/dk_Dinosaurs_and_Other_Prehistoric_Life')


@dp.message_handler()
async def echo(message: types.Message):
    await message.answer(message.text)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

