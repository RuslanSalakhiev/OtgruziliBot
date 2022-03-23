from datetime import date
from time import sleep
import requests
from bs4 import BeautifulSoup
import emoji

from data import add_book, find_publisher, find_book, add_publisher,print_books,get_all_publishers
import config
from bot import send_to_channel
from parsers import all_parsers as ps


def update_db(db_name, books, publisher_id):
    update_count = 0

    if books == []:   # Проверяю отдает ли что-то парсер
        return update_count

    for book in books:
        try:
            add_book(db_name,title=book[0],
                     publisher_id=publisher_id,
                     author=book[2],
                     release_date=date.today(),
                     short_abstract=book[4],
                     long_abstract=book[5],
                     url=book[1],
                     image_path=book[3])
            update_count += 1
        except:
            pass
    return update_count



def check_status(parsed,to_parse, total,update_count, status_message, publisher_name):
    # выравнивание длины строки
    print_publisher = "{:<16}".format(publisher_name)

    status = emoji.emojize(":green_book:") if total > 0 and to_parse == parsed and parsed == update_count else  emoji.emojize(":closed_book:")

    total = ' '+str(total) if len(str(total))==1 else total
    status_message = status_message + f"<code><b>{status}{print_publisher}:</b>{total}/{to_parse}→{parsed}→{update_count}\n</code>"

    return status_message

def parser_selector(db_name, publisher_name):
    #  выбор нужного парсера
    if publisher_name == 'МИФ':
        return ps.mif(config.db_name, publisher_name)
    elif publisher_name == 'Corpus':
        return ps.corpus(config.db_name, publisher_name)
    elif publisher_name == 'Бумкнига':
        return ps.boom(config.db_name, publisher_name)
    elif publisher_name == 'Альпина':
        return ps.alpina(config.db_name, publisher_name)
    elif publisher_name == 'Поляндрия':
        return ps.polyandria(config.db_name, publisher_name)
    elif publisher_name == 'Clever':
        return ps.clever(config.db_name, publisher_name)
    elif publisher_name == 'Азбука-Аттикус':
        return ps.azbuka(config.db_name, publisher_name)
    elif publisher_name == 'Карьера Пресс':
        return ps.career(config.db_name, publisher_name)
    elif publisher_name == 'Бомбора':
        return ps.bombora(config.db_name, publisher_name)
    elif publisher_name == 'Эксмо':
        return ps.eksmo(config.db_name, publisher_name)
    elif publisher_name == 'Эксмодетство':
        return ps.eksmo_det(config.db_name, publisher_name)
    elif publisher_name == 'Комильфо':
        return ps.komilfo(config.db_name, publisher_name)
    elif publisher_name == 'fanzon':
        return ps.fanzon(config.db_name, publisher_name)
    else:
        return [],0,0,0


today = date.today().strftime("%d/%m")
status_message = f"{today}\nСайт(All/New)→ Парсер → БД\n"

if __name__ == '__main__':
    # add_publisher(config.db_name, 'AD Marginem','https://admarginem.ru/')  # вручную добавить паблишера

    publisher_list = [{ 'name':p['name'], 'publisher_id':p['id']} for p in get_all_publishers(config.db_name)]

    for publisher in publisher_list:
        # парсинг
        books, parsed,to_parse, total  = parser_selector(config.db_name,publisher['name'])

        # получение file_id и перезапись image_url
        for idx,book in enumerate(books):
            try:
                books[idx][3]= send_to_channel(photo_url=book[3],message_type='photo', chat_id= config.tech_chat_id)
            except:
                # странный баг по Эксмо: при отправке фото в канал какие то падают с ошибкой, тогда подменяю урл фото
                books[idx][3] = send_to_channel(photo_url=book[3].replace('410','820'),message_type='photo', chat_id= config.tech_chat_id)
            sleep(4)
        # добавление в бд
        update_count = update_db(config.db_name, books,publisher['publisher_id'] )
        # формирование сообщения
        status_message = check_status(parsed,to_parse, total,update_count,status_message,publisher['name'])
    #отправка в бот
    send_to_channel(text = status_message,message_type='text', chat_id= config.tech_chat_id )
