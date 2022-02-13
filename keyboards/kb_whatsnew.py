from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def main_menu_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(text="Посмотреть новинки", callback_data="whatsnew"),
        InlineKeyboardButton(text="Подписаться на новинки", callback_data="subscribe"),
        InlineKeyboardButton(text="Управлять подписками", callback_data="manage_subscription"),
        InlineKeyboardButton(text="Help", callback_data="help")
    ]
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard

# Whatsnew

def select_period_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(text="За неделю", callback_data="7"),
        InlineKeyboardButton(text="За месяц", callback_data="30")
    ]
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard


# def select_publisher_keyboard(publishers) -> InlineKeyboardMarkup:
#     buttons = [
#         InlineKeyboardButton(text="МИФ", callback_data="МИФ"),
#         InlineKeyboardButton(text="Альпина", callback_data="Альпина"),
#         InlineKeyboardButton(text="Corpus", callback_data="Corpus"),
#         InlineKeyboardButton(text="Бумкнига", callback_data="Бумкнига")
#     ]
#     keyboard = InlineKeyboardMarkup(row_width=1)
#     keyboard.add(*buttons)
#     return keyboard


def select_publisher_keyboard(publishers) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()

    for pub in publishers:
        if pub['newbooks'] >0:
            btn = InlineKeyboardButton(text=f"{pub['name']}: {pub['newbooks']} книг", callback_data=pub['id'])
            keyboard.row(btn)

    return keyboard

def book_mode_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(text="Списком", callback_data="list"),
        InlineKeyboardButton(text="По одной", callback_data="count_incr")
    ]
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard


def show_book_keyboard(url) -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(text="Дальше", callback_data="count_incr"),
        InlineKeyboardButton(text="Назад ", callback_data="count_decr"),
        InlineKeyboardButton(text="На сайт", url=url),
    ]
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard


# Subscribe