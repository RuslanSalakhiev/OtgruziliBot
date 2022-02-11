from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram import types
import data
import config


# main -> /Unsubscribe -> unsubscribe_publishers -> МИФ/Альпина -> main
class BranchStates(StatesGroup):
    # /Subscribe chain:
    # main -> /Subscribe -> subscribe_publishers -> МИФ/Альпина ->
    # -> subscribe_perido -> Месяц/неделя -> main
    select_publisher = State()
    select_period = State()
    current_publisher = None

# @dp.message_handler(commands=['subscribe'])
async def start_subscribe(message: types.Message):
    publishers = data.get_all_publishers(config.db_name)
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
    for p in publishers:
        markup.add(p['name'])
    await BranchStates.select_publisher.set()
    await message.answer('На какое издательство подписаться?',
                         reply_markup=markup)


# @dp.message_handler(state=BranchStates.select_publisher)
async def process_publisher(message: types.Message):
    publishers = [p['name'] for p in data.get_all_publishers(config.db_name)]
    if message.text in publishers:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, selective=True)
        markup.add("Раз в месяц", "Раз в неделю")
        BranchStates.current_publisher = message.text
        await BranchStates.select_period.set()
        await message.answer("Как часто присылать уведомления?", reply_markup=markup)
    else:
        await message.answer('Такого издательства не существует')


# @dp.message_handler(state=BranchStates.select_period)
async def process_period(message: types.Message):
    if message.text.lower() in {"раз в месяц", "месяц"}:
        period = "0 10 1 * *"
    elif message.text.lower() in {"раз в неделю", "неделя"}:
        period = period = "0 10 * * 1"
    else:
        await message.answer('Выбран неверный период, допустимые значения: \
                             раз в месяц, раз в неделю')
        return
    # add subscription to database
    data.add_subscription(config.db_name, message.from_user.id, BranchStates.current_publisher, period)
    # await Root.main.set()
    await message.answer(f"Вы, {message.from_user.username}, подписаны на издательство {BranchStates.current_publisher}",
                         reply_markup=types.ReplyKeyboardRemove())
    BranchStates.current_publisher = None
