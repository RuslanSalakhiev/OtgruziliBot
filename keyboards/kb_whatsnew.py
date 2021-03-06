from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import emoji

def navigation_buttons(previous_step):
    buttons = [
        InlineKeyboardButton(text=emoji.emojize(":right_arrow_curving_up:")+" В меню", callback_data='navi_start'),
        InlineKeyboardButton(text=emoji.emojize(":left_arrow:")+" Назад", callback_data='navi_'+previous_step),
    ]
    return buttons

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

def select_period_keyboard(previous_step) -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(text="За неделю", callback_data="7"),
        InlineKeyboardButton(text="За месяц", callback_data="30")
    ]
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    keyboard.row(*navigation_buttons(previous_step))
    return keyboard


def select_publisher_keyboard(publishers,previous_step) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    for pub in publishers:
        if pub['newbooks'] >0:
            btn = InlineKeyboardButton(text=f"{pub['name']}: {pub['newbooks']} книг", callback_data=pub['id'])
            keyboard.row(btn)
    keyboard.row(*navigation_buttons(previous_step))
    return keyboard

def book_mode_keyboard(previous_step) -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(text="Списком", callback_data="list"),
        InlineKeyboardButton(text="По одной", callback_data="count_incr")
    ]
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    keyboard.row(*navigation_buttons(previous_step))
    return keyboard


def show_list_keyboard(books,previous_step) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup()
    for index,book in enumerate(books):
        btn = InlineKeyboardButton(text=f" {index+1}.{book['title']}. {book['author']}", callback_data='count_'+str(index+1))
        keyboard.row(btn)
    keyboard.row(*navigation_buttons(previous_step))
    return keyboard


def show_book_keyboard(url,previous_step) -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(text="Следующая", callback_data="count_incr"),
        InlineKeyboardButton(text="Предыдущая", callback_data="count_decr"),
        # InlineKeyboardButton(text="Полное описание", callback_data="description"),
        InlineKeyboardButton(text="На сайт", url=url)

    ]
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    keyboard.row(*navigation_buttons(previous_step))
    return keyboard

def send_to_channel_keyboard(url) -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(text="На сайт", url=url)

    ]
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(*buttons)
    return keyboard

# Subscribe