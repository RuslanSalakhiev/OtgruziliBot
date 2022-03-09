from time import sleep
import requests
from bs4 import BeautifulSoup
import logging
from selenium.webdriver import Chrome
from datetime import date

import config
from data import find_book

logging.basicConfig(filename='parsers.log', force=True, filemode='a', level=logging.ERROR)
today = date.today().strftime("%d/%m")

def get_catalog_xml(parser: str):
    url = ''
    if parser == 'МИФ':
        url = 'https://www.mann-ivanov-ferber.ru/books/new/'
    elif parser == 'Corpus':
        url = 'https://www.corpus.ru/products/novinki/'
    elif parser == 'Бумкнига':
        url = 'https://boomkniga.ru/shop/'
    # elif parser == 'Альпина':
    #     url = 'https://alpinabook.ru/catalog/filter/new-is-new-books-only/apply/'
    elif parser == 'Поляндрия':
        url = 'https://polyandria.ru/catalog/novinki/'
    elif parser == 'Clever':
        url = 'https://www.clever-media.ru/books/filter/priznak-is-1/apply/?SORT=property_DATE_PUBLICATION_SORT%7CDESC'
    # elif parser == 'Азбука-Аттикус':
    #     url = 'https://azbooka.ru/catalog/'
    elif parser == 'Карьера Пресс':
        url = 'https://careerpress.ru/books/new/'
    elif parser == 'Бомбора':
        url = 'https://eksmo.ru/book/?sort=date&novinka[]=1&available[]=2&format[]=p&publisher[]=1192'
    elif parser == 'Эксмо':
        url = 'https://eksmo.ru/book/?sort=date&novinka[]=1&available[]=2&format[]=p&publisher[]=603'
    elif parser == 'Эксмодетство':
        url = 'https://eksmo.ru/book/?sort=date&novinka[]=1&available[]=2&format[]=p&publisher[]=1198'
    elif parser == 'Комильфо':
        url = 'https://eksmo.ru/book/?sort=date&novinka[]=1&available[]=2&format[]=p&publisher[]=1193'
    elif parser == 'fanzon':
        url = 'https://eksmo.ru/book/?sort=date&novinka[]=1&available[]=2&format[]=p&publisher[]=1181'

    if url == '':
        logging.error(f"{today}-{parser}-get_catalog_xml-No url for this parser")
        return ''

    try:
        r = requests.get(url)
    except Exception as E:
        logging.error(f"{today}-{parser}-get_catalog_xml-{str(E)}")

    return BeautifulSoup(r.text, 'lxml')


def get_list_of_books(parser: str, catalog_xml):
    books = ''
    try:
        if parser == 'МИФ':
            books = catalog_xml.find('div', class_='c-page-new-best-soon m-new').find('div').findAll('div',
                                                                                                     class_='lego-book')
        elif parser == 'Corpus':
            books = catalog_xml.findAll('div', class_='book__item__container')
        elif parser == 'Бумкнига':
            books = catalog_xml.findAll('div', class_='grid_item')
        # elif parser == 'Альпина':
        #     books = catalog_xml.findAll('div', class_='b-book-v__pic')
        elif parser == 'Поляндрия':
            books = catalog_xml.findAll('div', class_='books-item__content')
        elif parser == 'Clever':
            books = catalog_xml.findAll('div', class_='book-preview')
        # elif parser == 'Азбука-Аттикус':
        #     books = catalog_xml.findAll('li', class_='_1k6ALYz7TO')
        elif parser == 'Карьера Пресс':
            books = catalog_xml.findAll('div', class_='span4 teaser-box book-teaser-box')
        elif parser in ('Эксмо', 'Эксмодетство', 'Комильфо', 'fanzon', 'Бомбора'):
            books = catalog_xml.findAll('div', class_='books__item')
    except Exception as E:
        logging.error(f"{today}-{parser}-get_list_of_books-{str(E)}")

    return books


def get_list_of_newbooks (parser, book_urls, db_name):
    exceptions = ['https://boomkniga.ru/shop/other/boom-karta/', 'https://boomkniga.ru/shop/other/bumshoper-belyj/',
                  'https://boomkniga.ru/shop/other/bumshoper-chernyj/', 'https://polyandria.ru/catalog/novinki/candle/']
    newbook_urls = []
    newbook_urls.extend(book_urls)
    try:
        for book_url in book_urls:
            if find_book(db_name, book_url) is not None or book_url in exceptions:
               newbook_urls.remove(book_url)
    except Exception as E:
        logging.error(f"{today}-{parser}-get_list_of_newbooks-{str(E)}")
    return newbook_urls


def get_bookpage_xml(parser: str, list_of_newbooks):
    list_of_bookpage_xml = []
    try:
        for book_url in list_of_newbooks:
            r = requests.get(book_url)
            if parser in ('Эксмо', 'Эксмодетство', 'Комильфо', 'fanzon', 'Бомбора'):   #для издательств с прогружаемыми элементами нужен selenium
                browser = Chrome('parsing/chromedriver')
                browser.get(book_url)
                sleep(2)
                list_of_bookpage_xml.append(BeautifulSoup(browser.page_source, 'lxml'))
                browser.close()
            else:
                list_of_bookpage_xml.append(BeautifulSoup(r.text, 'lxml'))
    except Exception as E:
        logging.error(f"{today}-{parser}-get_bookpage_xml-{book_url}-{str(E)}")
    return list_of_bookpage_xml


def get_book_url(parser: str, list_of_books):
    list_of_urls = []
    book_url = ''

    for book in list_of_books:
        try:
            if parser == 'МИФ':
                book_url = book.find('a', class_='lego-book__cover').get('href')
            elif parser == 'Corpus':
                book_url = book.find('a').get('href')
            elif parser == 'Бумкнига':
                book_url = book.find('a').get('href')
            # elif parser == 'Альпина':
            #     book_url = 'https://alpinabook.ru' + book.find('a').get('href')
            elif parser == 'Поляндрия':
                book_url = 'https://polyandria.ru' + book.find('a').get('href')
            elif parser == 'Clever':
                book_url = 'https://www.clever-media.ru' + book.find('a', class_='js-item').get('href')
            # elif parser == 'Азбука-Аттикус':
            #     book_url = 'https://azbooka.ru' + book.find('a', class_='_1xZtrM_AjY').get('href')
            elif parser == 'Карьера Пресс':
                book_url = 'https://careerpress.ru' + book.find('a').get('href')
            elif parser in ('Эксмо', 'Эксмодетство', 'Комильфо', 'fanzon', 'Бомбора'):
                book_url = 'https://eksmo.ru' + book.find('a', class_='book__link').get('href')

            list_of_urls.append(book_url)
        except Exception as E:
            logging.error(f"{today}-{parser}-get_book_url-{book_url}-{str(E)}")

    return list_of_urls


def get_book_image(parser: str, bookpage_xml, book_url):
    image_url = ''
    try:
        if parser == 'МИФ':
            if bookpage_xml.find('div', class_='img-wrapper') is not None:
                image_url ='https://www.mann-ivanov-ferber.ru/' + bookpage_xml.find('div', class_='img-wrapper').find('img').get('src')
            else:
                image_url ='https://www.mann-ivanov-ferber.ru/' + bookpage_xml.find('div', class_='img-wrap').find('img').get('src')
        elif parser == 'Corpus':
            image_url = 'https://www.corpus.ru' + bookpage_xml.find('div', class_='productzoom__top__info__image').find(
                'img').get('src')
        elif parser == 'Бумкнига':
            image_url = bookpage_xml.find('div', class_='woocommerce-product-gallery__image').find('a').get('href')
        # elif parser == 'Альпина':
        #     image_url = 'https://alpinabook.ru' + book.find('img').get('src')
        elif parser == 'Поляндрия':
            image_url = 'https://polyandria.ru' + bookpage_xml.find('div', class_='book__cover').find('img').get('src')
        elif parser == 'Clever':
            image_url = 'https://www.clever-media.ru' + bookpage_xml.find('div', class_='m1').find('img').get('src')
        # elif parser == 'Азбука-Аттикус':
        #     image_url = bookpage_xml.find('div', class_='_2vaQTYoxdK').get('style').replace('background-image:url(','').replace(')', '')
        elif parser == 'Карьера Пресс':
            image_url = bookpage_xml.find('img', class_='bookcover').get('src')
        elif parser in ('Эксмо', 'Эксмодетство', 'Комильфо', 'fanzon', 'Бомбора'):
            image_url = bookpage_xml.find('img', class_='book-page__cover-pic').get('srcset').split(' ')[2]
    except Exception as E:
        logging.error(f"{today}-{parser}-get_book_image-{book_url}-{str(E)}")

    return image_url


def get_title(parser: str, bookpage_xml, book_url):
    title = ''

    try:
        if parser == 'МИФ':
            title = bookpage_xml.find('h1', class_='header active p-sky-title').text
        elif parser == 'Corpus':
            title = bookpage_xml.find('h1', class_='productzoom__name hidden-xs').text.strip()
        elif parser == 'Бумкнига':
            title = bookpage_xml.find('div', class_='summary entry-summary').find('h1').text.strip()
        # elif parser == 'Альпина':
        #     title = bookpage_xml.find('span', class_='b-book-primary__title-main').text
        elif parser == 'Поляндрия':
            title = bookpage_xml.find('div', class_='book-info__content').find('h1').text
        elif parser == 'Clever':
            title = bookpage_xml.find('div', class_='blocks').find('div', class_='top').find('h1').text
        # elif parser == 'Азбука-Аттикус':
        #     title = book.find('img').get('title')
        elif parser == 'Карьера Пресс':
            title = bookpage_xml.find('h1', class_='title').text
        elif parser in ('Эксмо', 'Эксмодетство', 'Комильфо', 'fanzon', 'Бомбора'):
            title = bookpage_xml.find('h1', class_='book-page__card-title').text
    except Exception as E:
        logging.error(f"{today}-{parser}-get_title-{book_url}-{str(E)}")

    return title


def get_author(parser: str, bookpage_xml, book_url):
    author = ''
    author_list = []
    try:
        if parser == 'МИФ':
            for one_author in bookpage_xml.find('div', class_='authors').findAll('span', class_='author active'):
                author_list.append(one_author.text)
            author = ', '.join(author_list)
        elif parser == 'Corpus':
            for one_author in bookpage_xml.find('div', class_='productzoom__author hidden-xs').findAll('a'):
                author_list.append(one_author.text)
            author = ', '.join(author_list)
        elif parser == 'Бумкнига':
            for one_author in bookpage_xml.find('div', class_='pwb-single-product-brands pwb-clearfix').findAll('a'):
                author_list.append(one_author.text)
            author = ', '.join(author_list)
        # elif parser == 'Альпина':
        #     authors = bookpage_xml.find('div', class_='b-book-primary__authors').findAll('a')
        elif parser == 'Поляндрия':
            for one_author in bookpage_xml.find('div', class_='book__description').find('dd').findAll('a'):
                author_list.append(one_author.text)
            author = ', '.join(author_list)
        elif parser == 'Clever':
            for author_block in bookpage_xml.find('div', class_='block product-card-description').findAll('div',
                                                                                                          class_='form-group'):
                try:
                    if author_block.find('div', class_='label line').text == 'Автор:':
                        authors = author_block.findAll('a')
                        break
                except:
                    pass
            for one_author in authors:
                author_list.append(one_author.text)
            author = ', '.join(author_list)
        # elif parser == 'Азбука-Аттикус':
        #     for one_author in bookpage_xml.find('div', itemprop='author').findAll('a'):
        #         author_list.append(one_author.text)
        #     author = ', '.join(author_list)
        elif parser == 'Карьера Пресс':
            authors = [a for a in bookpage_xml.find('div', class_='span10').findAll('a') if a.get('href')[:7] == '/author']
            for one_author in authors:
                author_list.append(one_author.text)
            author = ', '.join(author_list)
        elif parser in ('Эксмо', 'Эксмодетство', 'Комильфо', 'fanzon', 'Бомбора'):
            if bookpage_xml.find('div', class_='book-page__card-author') == None:
                author = ''
            else:
                authors = bookpage_xml.find('div', class_='book-page__card-author').findAll('a')
                for one_author in authors:
                    author_list.append(one_author.text)
                author = ', '.join(author_list)
    except Exception as E:
        logging.error(f"{today}-{parser}-get_author-{book_url}-{str(E)}")

    return author


def get_abstract(parser: str, bookpage_xml, book_url):
    short_abstract = ''
    full_abstract = ''
    abstract_block = ''
    try:
        if parser == 'МИФ':
            abstract_block = bookpage_xml.find('div', class_='b-expand').find('div').find('div').findAll()
            short_abstract = abstract_block[0].text
        elif parser == 'Corpus':
            abstract_block = bookpage_xml.find('div', class_='rowBlockText').findAll()
            short_abstract = abstract_block[0].text
        elif parser == 'Бумкнига':
            abstract_block = bookpage_xml.find('div', class_='woocommerce-Tabs-panel').findAll('p')
            short_abstract = abstract_block[1].text
        # elif parser == 'Альпина':
        #     abstract_block = bookpage_xml.find('section', class_='book-content-section').findAll()
        #     short_abstract = abstract_block[0].text
        elif parser == 'Поляндрия':
            abstract_block = bookpage_xml.find('div', class_='book-info__preview-text').findAll()
            short_abstract = abstract_block[0].text
        elif parser == 'Clever':
            abstract_block = bookpage_xml.find('div', class_='tab-pane', id='productDescription').findAll()
            short_abstract = abstract_block[1].text
        # elif parser == 'Азбука-Аттикус':
        #     abstract_block = bookpage_xml.find('div', class_='wth2ozwagb').findAll()
        #     short_abstract = abstract_block[0].text
        elif parser == 'Карьера Пресс':
            # корявый сайт
            short_abstract = ''
            full_abstract = ''
        elif parser in ('Эксмо', 'Эксмодетство', 'Комильфо', 'fanzon', 'Бомбора'):
            abstract_block = bookpage_xml.find('div', class_='spoiler__text').findAll()
            short_abstract = abstract_block[0].text
    except Exception as E:
        logging.error(f"{today}-{parser}-get_abstract-{book_url}-{str(E)}")

    for text_part in abstract_block:
        full_abstract = full_abstract + text_part.text + '\n'

    return short_abstract, full_abstract


def parse(publisher_name: str):
    parsed_books = []

    catalog_xml = get_catalog_xml(publisher_name)
    if catalog_xml == '':
        return [],0,0,0

    list_of_books = get_list_of_books(publisher_name, catalog_xml)
    book_urls = get_book_url(publisher_name, list_of_books)
    list_of_newbooks = get_list_of_newbooks(publisher_name, book_urls, config.db_name)
    list_of_bookpage_xml = get_bookpage_xml(publisher_name, list_of_newbooks)

    for idx, book_xml in enumerate(list_of_bookpage_xml):
        book_url = list_of_newbooks[idx]
        title = get_title(publisher_name, book_xml, book_url)
        author = get_author(publisher_name, book_xml, book_url)
        short_abstract, full_abstract = get_abstract(publisher_name, book_xml, book_url)
        image_url = get_book_image(publisher_name, book_xml, book_url)

        parsed_books.append([title, book_url , author, image_url, short_abstract, full_abstract, publisher_name])
        sleep(2)

    return parsed_books, len(parsed_books), len(list_of_newbooks), len(list_of_books)
