from datetime import date
from time import sleep
import requests
from bs4 import BeautifulSoup


from data import add_book, find_publisher, find_book, add_publisher,print_books,get_all_publishers

def alpina(db_name, publisher_name):
    url = 'https://alpinabook.ru/catalog/filter/new-is-new-books-only/apply/'

    r = requests.get(url)
    catalog_xml = BeautifulSoup(r.text, 'lxml')
    books = catalog_xml.findAll('div', class_='b-book-v__pic')

    data = []
    to_parse = 0
    # парсинг каталога новинок
    for book in books:
        book_url = 'https://alpinabook.ru' + book.find('a').get('href')

        image_url = 'https://alpinabook.ru' + book.find('img').get('src')
        if find_book(db_name, book_url) is None:
            to_parse += 1
            try:
                # парсинг страницы книги

                r = requests.get(book_url)
                bookpage_xml = BeautifulSoup(r.text, 'lxml')

                title = bookpage_xml.find('span', class_='b-book-primary__title-main').text

                authors = bookpage_xml.find('div', class_='b-book-primary__authors').findAll('a')
                author_list = []
                for one_author in authors:
                    author_list.append(one_author.text)
                author = ','.join(author_list)

                bookpage = bookpage_xml.find('section', class_='book-content-section')

                abstract_block = bookpage.findAll()

                short_abstract = abstract_block[0].text
                full_abstract = ''
                for text_part in abstract_block:
                    full_abstract = full_abstract + text_part.text + '\n'

                data.append([title, book_url, author, image_url, short_abstract, full_abstract, publisher_name])
            except:
                pass

            sleep(2)

    return data, len(data), to_parse, len(books)


def mif(db_name, publisher_name):
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
                    'img').get('data-original').replace('0.50x','1.00x')

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

                data.append([title, book_url, author, image_url, short_abstract, full_abstract, publisher_name])
            except:
                pass

            sleep(2)

    return data, len(data), to_parse, len(books)


def corpus(db_name, publisher_name):
    url = 'https://www.corpus.ru/products/novinki/'

    r = requests.get(url)
    catalog_xml = BeautifulSoup(r.text, 'lxml')

    books = catalog_xml.findAll('div', class_='book__item__container')

    data = []
    to_parse = 0
    # парсинг каталога новинок
    for book in books:
        book_url = book.find('a').get('href')

        if find_book(db_name, book_url) is None:
            to_parse += 1
            try:
                title = book.find('div', class_='book__item__title').find('span').text.strip()
                author = book.find('div', class_='book__item__author').find('span').text

                r = requests.get(book_url)
                bookpage_xml = BeautifulSoup(r.text, 'lxml')

                image_url ='https://www.corpus.ru'+ bookpage_xml.find('div', class_='productzoom__top__info__image').find('img').get('src')

                abstract_block = bookpage_xml.find('div', class_='rowBlockText').findAll()

                short_abstract = abstract_block[0].text

                full_abstract = ''
                for text_part in abstract_block:
                    full_abstract = full_abstract + text_part.text + '\n'


                data.append([title, book_url, author, image_url, short_abstract, full_abstract, publisher_name])

            except:
                pass

            sleep(2)
    return data, len(data), to_parse, len(books)


def boom(db_name, publisher_name):
    # список урлов некниг ()
    exceptions = ['https://boomkniga.ru/shop/other/boom-karta/', 'https://boomkniga.ru/shop/other/bumshoper-belyj/',
                  'https://boomkniga.ru/shop/other/bumshoper-chernyj/']
    url = 'https://boomkniga.ru/shop/'

    r = requests.get(url)
    catalog_xml = BeautifulSoup(r.text, 'lxml')

    # парсинг каталога новинок
    books = catalog_xml.findAll('div', class_='grid_item')

    data = []
    to_parse = 0

    for book in books:
        book_url = book.find('a').get('href')

        # парсинг страницы книги
        if find_book(db_name, book_url) is None and book_url not in exceptions:
            to_parse += 1
            try:
                r = requests.get(book_url)
                bookpage_xml = BeautifulSoup(r.text, 'lxml')

                title = bookpage_xml.find('div', class_='summary entry-summary').find('h1').text.strip()
                image_url = bookpage_xml.find('div', class_='woocommerce-product-gallery__image').find('a').get('href')

                authors = bookpage_xml.find('div', class_='pwb-single-product-brands pwb-clearfix').findAll('a')
                author_list = []
                for one_author in authors:
                    author_list.append(one_author.text)
                author = ','.join(author_list)

                abstract_block = bookpage_xml.find('div', class_='woocommerce-Tabs-panel').findAll('p')
                short_abstract = abstract_block[1].text
                full_abstract = ''
                for text_part in abstract_block:
                    full_abstract = full_abstract + text_part.text + '\n'
                data.append([title, book_url, author, image_url, short_abstract, full_abstract, publisher_name])

            except:
                pass

            sleep(2)

    return data, len(data), to_parse, len(books)

def polyandria(db_name, publisher_name):
    exceptions = ['https://polyandria.ru/catalog/novinki/candle/']
    url = 'https://polyandria.ru/catalog/novinki/'

    r = requests.get(url)
    catalog_xml = BeautifulSoup(r.text, 'lxml')
    books = catalog_xml.findAll('div', class_='books-item__content')

    data = []
    to_parse = 0
    # парсинг каталога новинок
    for book in books:
        book_url = 'https://polyandria.ru' + book.find('a').get('href')

        title = book.find('div', class_='book__item__name').find('a').get('title')
        author = '' if book.find('div', class_='book__item__autor').text is None else book.find('div',
                                                                                                class_='book__item__autor').text

        if find_book(db_name, book_url) is None and book_url not in exceptions:
            to_parse += 1
            try:
                # парсинг страницы книги
                r = requests.get(book_url)

                bookpage_xml = BeautifulSoup(r.text, 'lxml')

                image_url = 'https://polyandria.ru' + bookpage_xml.find('div',class_='book__cover').find('img').get('src')
                bookpage = bookpage_xml.find('div', class_='book-info__preview-text')


                abstract_block = bookpage.findAll()

                short_abstract = abstract_block[0].text
                full_abstract = ''
                for text_part in abstract_block:
                    full_abstract = full_abstract + text_part.text + '\n'

                data.append([title, book_url, author, image_url, short_abstract, full_abstract, publisher_name])
            except:
                pass

            sleep(2)
    return data, len(data), to_parse, len(books)

def clever(db_name, publisher_name):
    # список урлов некниг ()
    exceptions = []
    url = 'https://www.clever-media.ru/books/filter/priznak-is-1/apply/?SORT=property_DATE_PUBLICATION_SORT%7CDESC'
    r = requests.get(url)
    catalog_xml = BeautifulSoup(r.text, 'lxml')
    books = catalog_xml.findAll('div', class_='book-preview')

    data = []
    to_parse = 0
    # парсинг каталога новинок
    for book in books:
        book_url = 'https://www.clever-media.ru' + book.find('a', class_='js-item').get('href')

        title = book.find('div', class_='book-name').find('a').get('data-name')
        author = '' if book.find('div', class_='author right_b').text is None else book.find('div',
                                                                                                class_='author right_b').text

        if find_book(db_name, book_url) is None and book_url not in exceptions:
            to_parse += 1
            try:
                # парсинг страницы книги
                r = requests.get(book_url)

                bookpage_xml = BeautifulSoup(r.text, 'lxml')

                image_url = 'https://www.clever-media.ru' + bookpage_xml.find('div', class_='m1').find('img').get('src')
                bookpage = bookpage_xml.find('div', class_='tab-pane', id='productDescription')

                abstract_block = bookpage.findAll()

                short_abstract = abstract_block[1].text
                full_abstract = ''
                for text_part in abstract_block:
                    full_abstract = full_abstract + text_part.text + '\n'

                data.append([title, book_url, author, image_url, short_abstract, full_abstract, publisher_name])
            except:
                pass

            sleep(2)
    return data, len(data), to_parse, len(books)


def azbuka(db_name, publisher_name):
    # список урлов некниг ()
    exceptions = []
    url = 'https://azbooka.ru/catalog/'
    r = requests.get(url)
    catalog_xml = BeautifulSoup(r.text, 'lxml')
    books = catalog_xml.findAll('li', class_='_1k6ALYz7TO')

    data = []
    to_parse = 0
    # парсинг каталога новинок
    for book in books:
        book_url = 'https://azbooka.ru' + book.find('a', class_='_1xZtrM_AjY').get('href')
        title = book.find('img').get('title')

        if find_book(db_name, book_url) is None and book_url not in exceptions:
            to_parse += 1
            try:
                # парсинг страницы книги
                r = requests.get(book_url)

                bookpage_xml = BeautifulSoup(r.text, 'lxml')

                authors = bookpage_xml.find('div',itemprop='author').findAll('a')
                author_list = []
                for one_author in authors:
                    author_list.append(one_author.text)
                author = ','.join(author_list)

                image_url = bookpage_xml.find('div', class_='_2vaQTYoxdK').get('style').replace('background-image:url(','').replace(')','')

                bookpage = bookpage_xml.find('div', class_='wth2ozwagb')

                abstract_block = bookpage.findAll()

                short_abstract = abstract_block[0].text
                full_abstract = ''
                for text_part in abstract_block:
                    full_abstract = full_abstract + text_part.text + '\n'

                data.append([title, book_url, author, image_url, short_abstract, full_abstract, publisher_name])
            except:
                pass

            sleep(2)
    return data, len(data), to_parse, len(books)

def career(db_name, publisher_name):
    # список урлов некниг ()
    exceptions = []
    url = 'https://careerpress.ru/books/new/'
    r = requests.get(url)
    catalog_xml = BeautifulSoup(r.text, 'lxml')
    books = catalog_xml.findAll('div', class_='span4 teaser-box book-teaser-box')

    data = []
    to_parse = 0
    # парсинг каталога новинок
    for book in books:
        book_url = 'https://careerpress.ru' + book.find('a').get('href')
        title = book.find('h4').text

        authors = book.find('p').findAll('a')
        author_list = []
        for one_author in authors:
            author_list.append(one_author.text)
        author = ','.join(author_list)


        if find_book(db_name, book_url) is None and book_url not in exceptions:
            to_parse += 1
            try:
                # парсинг страницы книги
                r = requests.get(book_url)

                bookpage_xml = BeautifulSoup(r.text, 'lxml')

                image_url = bookpage_xml.find('img',class_='bookcover').get('src')

                bookpage = bookpage_xml.find('div', class_='span-two-thirds')

                abstract_block = bookpage.findAll()

                short_abstract = abstract_block[0].text
                full_abstract = ''
                for text_part in abstract_block:
                    full_abstract = full_abstract + text_part.text + '\n'

                data.append([title, book_url, author, image_url, short_abstract, full_abstract, publisher_name])
            except:
                pass

            sleep(2)
    return data, len(data), to_parse, len(books)

