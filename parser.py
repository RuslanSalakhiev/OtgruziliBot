from datetime import date
from time import sleep
import requests
from bs4 import BeautifulSoup

from data import add_book, find_publisher, find_book
import config
from bot import send_to_channel


def parse_mif(db_name, publisher_name):
    url = 'https://www.mann-ivanov-ferber.ru/books/new/'

    r = requests.get(url)
    catalog_xml = BeautifulSoup(r.text, 'lxml')
    books = catalog_xml.find('div', class_='c-page-new-best-soon m-new').find('div').findAll('div', class_='lego-book')

    data = []
    to_parse = 0
    # парсинг каталога новинок
    for book in books:
        book_url = book.find('a', class_='lego-book__cover').get('href')

        if find_book(db_name, book_url) is None:
            to_parse +=1
            try:

                image_url = 'https://www.mann-ivanov-ferber.ru/' + book.find('a', class_='lego-book__cover').find(
                    'img').get('data-original').replace('0.50x', '2.00x')

                title = book.find('div', class_='lego-book__cover-loading-title').findAll('p')[0].text
                author = book.find('div', class_='lego-book__cover-loading-title').findAll('p')[1].text

                # парсинг страницы книги

                r = requests.get(book_url)
                bookpage_xml = BeautifulSoup(r.text, 'lxml')

                bookpage = bookpage_xml.find('div', class_='b-expand')

                abstract_block = bookpage.find('div').find('div').findAll()

                short_abstract = abstract_block[0].text.replace('\xa0','')
                full_abstract = ''
                for text_part in abstract_block:
                    full_abstract = full_abstract + text_part.text.replace('\xa0','') + '\n'

                data.append([title, book_url, author, image_url, short_abstract, full_abstract, publisher_name])
            except:
                pass

            sleep(2)

    return data, len(data), to_parse, len(books)

def update_db(db_name, books,publisher_name):
    update_count = 0

    if books == []:   # Проверяю отдает ли что-то парсер
        return update_count

    publisher_id = find_publisher(db_name,publisher_name).get('id')

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


def update_status(db_name, books):
    pass

def check_status(parsed,to_parse, total,update_count):
    status = 'ок' if total > 0 and to_parse == parsed and parsed == update_count else 'alarm!!!'
    return status

if __name__ == '__main__':
    today = date.today().strftime("%d/%m")

    # Парсинг МИФа
    publisher_name = 'МИФ'
    books, parsed,to_parse, total  = parse_mif(config.db_name, publisher_name)
    update_count = update_db(config.db_name, books, publisher_name)
    status = check_status(parsed,to_parse, total,update_count)

    text = str(f"{today}\n<b>{publisher_name}:</b> Парсер: {total}/{to_parse}/{parsed}. БД: {update_count} --- {status}")
    # Отправка статистики в канал
    send_to_channel(text)