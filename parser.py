import requests
from selenium.webdriver import Chrome
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait as wait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from time import sleep
import re
import pandas as pd


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

            short_abstract = abstract_block[0].text
            full_abstract = ''
            for text_part in abstract_block:
                full_abstract = full_abstract + text_part.text + '\n'

            data.append([title, book_url, author, image_url, short_abstract, full_abstract])
        except:
            pass

        sleep(2)

    print('Всего - ', len(books), '.')
    print('Обработано - ', len(data), '.')

    df = pd.DataFrame(data, columns=['title', 'book_url', 'author', 'image_url', 'short_abstract', 'full_abstract'])
    df.to_csv('data_mif.csv', encoding="utf-8-sig")


def update_db():
    pass

if __name__ == '__main__':
    parse_mif()

