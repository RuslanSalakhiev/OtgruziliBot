from datetime import date
from time import sleep
import requests
from bs4 import BeautifulSoup

from data import add_book, find_publisher, find_book
import config
from bot import send_to_channel

def parse_mif():
    url = 'https://www.mann-ivanov-ferber.ru/books/new/'

    r = requests.get(url)
    catalog_xml = BeautifulSoup(r.text, 'lxml')
    books = catalog_xml.find('div', class_='c-page-new-best-soon m-new').find('div').findAll('div', class_='lego-book')

    data = []

    # парсинг каталога новинок
    for book in books:
        try:
            book_url = book.find('a', class_='lego-book__cover').get('href')
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

            data.append([title, book_url, author, image_url, short_abstract, full_abstract,'МИФ'])
        except:
            pass

        sleep(2)

    return data, len(data), len(books)

def update_db(db_name, books,publisher_name):
    publisher_id = find_publisher(db_name,publisher_name).get('id')
    update_count = 0
    for book in books:
       if find_book(db_name, book[1]) is None:
            add_book(db_name,title=book[0],
                     publisher_id=publisher_id,
                     author=book[2],
                     release_date=date.today(),
                     short_abstract=book[4],
                     long_abstract=book[5],
                     url=book[1],
                     image_path=book[3])
            update_count += 1
    return update_count


def update_status(db_name, books):
    pass

if __name__ == '__main__':
    today = date.today().strftime("%d/%m")

    # Парсинг МИФа
    books, success,total = parse_mif()
    publisher_name = books[0][6]
    update_count = update_db(config.db_name, books, publisher_name)
    text = str(f"{today}. \n<b>{publisher_name}</b>. Парсер {success}/{total}. Запись в БД: {update_count}")

    # Отправка статистики в канал
    send_to_channel(text)
