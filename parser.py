from datetime import date
from time import sleep
import requests
from bs4 import BeautifulSoup
import emoji

from data import add_book, find_publisher, find_book, add_publisher,print_books,get_all_publishers
import config
from bot import send_to_channel

def parse_alpina(db_name, publisher_name):
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


def parse_mif(db_name, publisher_name):
    url = 'https://www.mann-ivanov-ferber.ru/books/new/'

    if find_publisher(db_name,publisher_name) is None: add_publisher(db_name, publisher_name)

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


def parse_corpus(db_name, publisher_name):
    url = 'https://www.corpus.ru/products/novinki/'

    if find_publisher(db_name, publisher_name) is None: add_publisher(db_name,  publisher_name)

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


def parse_boom(db_name, publisher_name):
    url = 'https://boomkniga.ru/shop/'

    if find_publisher(db_name, publisher_name) is None: add_publisher(db_name, publisher_name)

    r = requests.get(url)
    catalog_xml = BeautifulSoup(r.text, 'lxml')

    # парсинг каталога новинок
    books = catalog_xml.findAll('div', class_='grid_item')

    data = []
    to_parse = 0
    # список урлов некниг ()
    exceptions = ['https://boomkniga.ru/shop/other/boom-karta/','https://boomkniga.ru/shop/other/bumshoper-belyj/','https://boomkniga.ru/shop/other/bumshoper-chernyj/']

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
        return parse_mif(config.db_name, publisher_name)
    elif publisher_name == 'Corpus':
        return parse_corpus(config.db_name, publisher_name)
    elif publisher_name == 'Бумкнига':
        return parse_boom(config.db_name, publisher_name)
    elif publisher_name == 'Альпина':
        return parse_alpina(config.db_name, publisher_name)
    else:
        return [],0,0,0


today = date.today().strftime("%d/%m")
status_message = f"{today}\nСайт(All/New)→ Парсер → БД\n"

if __name__ == '__main__':
    add_publisher(config.db_name, 'AD Marginem','https://admarginem.ru/')  # вручную добавить паблишера
    add_publisher(config.db_name, 'Азбука-Аттикус','https://azbooka.ru')
    add_publisher(config.db_name, 'Редакция Елены Шубиной','https://ast.ru/redactions/redaktsiya-eleny-shubinoy/')
    add_publisher(config.db_name, 'РИПОЛ Классик','https://ripol.ru/')
    add_publisher(config.db_name, 'Клевер','https://www.clever-media.ru')
    add_publisher(config.db_name, 'Самокат','https://samokatbook.ru/')
    add_publisher(config.db_name, 'Карьера Пресс','https://careerpress.ru')
    add_publisher(config.db_name, 'Поляндрия','https://polyandria.ru')
    add_publisher(config.db_name, 'Мелик - Пашаев','https://melik-pashaev.online')
    add_publisher(config.db_name, 'Розовый жираф','https: // www.pgbooks.ru')
    add_publisher(config.db_name, 'Пешком в историю','https://www.peshkombooks.ru')
    add_publisher(config.db_name, 'Livebook','https://livebooks.ru')
    add_publisher(config.db_name, 'Фантом Пресс', 'https://phantom-press.ru')
    add_publisher(config.db_name, 'fanzon', 'https://fanzon-portal.ru')


    publisher_list = [{ 'name':p['name'], 'publisher_id':p['id']} for p in get_all_publishers(config.db_name)]

    for publisher in publisher_list:
        # парсинг
        books, parsed,to_parse, total  = parser_selector(config.db_name,publisher['name'])

        # получение file_id и перезапись image_url
        for idx,book in enumerate(books):
            books[idx][3]= send_to_channel(book[3],'photo')
            sleep(4)
        # добавление в бд
        update_count = update_db(config.db_name, books,publisher['publisher_id'] )
        # формирование сообщения
        status_message = check_status(parsed,to_parse, total,update_count,status_message,publisher['name'])
    #отправка в бот
    send_to_channel(status_message,'text')
