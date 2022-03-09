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
    added_to_db = 0

    if books == []:   # Проверяю отдает ли что-то парсер
        return added_to_db

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
            added_to_db += 1
        except:
            pass
    return added_to_db



def check_status(parsed,to_parse, found_on_site,added_to_db, status_message, publisher_name):
    # выравнивание длины строки
    print_publisher = "{:<16}".format(publisher_name)

    status = emoji.emojize(":green_book:") if found_on_site > 0 and to_parse == parsed and parsed == added_to_db else  emoji.emojize(":closed_book:")

    found_on_site = ' '+str(found_on_site) if len(str(found_on_site))==1 else found_on_site
    status_message = status_message + f"<code><b>{status}{print_publisher}:</b>{found_on_site}/{to_parse}→{parsed}→{added_to_db}\n</code>"

    return status_message




today = date.today().strftime("%d/%m")
status_message = f"{today}\nСайт(All/New)→ Парсер → БД\n"

if __name__ == '__main__':
    # add_publisher(config.db_name, 'AD Marginem','https://admarginem.ru/')  # вручную добавить паблишера

    publisher_list = [{ 'name':p['name'], 'publisher_id':p['id']} for p in get_all_publishers(config.db_name) if p['name'] not in ('Альпина','Азбука-Аттикус')]

    for publisher in publisher_list:
        # парсинг
        books, parsed,to_parse, found_on_site  = ps.parse(publisher['name'])

        # получение file_id и перезапись image_url
        for idx,book in enumerate(books):
            try:
                books[idx][3]= send_to_channel(photo_url=book[3],message_type='photo', chat_id= config.tech_chat_id)
            except:
                # странный баг по Эксмо: при отправке фото в канал какие то падают с ошибкой, тогда подменяю урл фото
                books[idx][3] = send_to_channel(photo_url=book[3].replace('410','820'),message_type='photo', chat_id= config.tech_chat_id)
            sleep(4)
        # добавление в бд
        added_to_db = update_db(config.db_name, books,publisher['publisher_id'] )
        # формирование сообщения
        status_message = check_status(parsed,to_parse, found_on_site,added_to_db,status_message,publisher['name'])

    #отправка в бот
    send_to_channel(text = status_message,message_type='text', chat_id= config.tech_chat_id )
