import sqlite3 as sql
import datetime as dt
import urllib.parse as urlparse

DB_NAME = "tg_bot.db"


def add_book(db_name, title, publisher_id, author, release_date,
             short_abstract=None, long_abstract=None,
             url=None,
             image_path=None):

    with sql.connect(db_name) as con:
        con.cursor().execute('''INSERT INTO book(
                            publisher_id, 
                            title, 
                            author,
                            release_date, 
                            short_abstract, 
                            long_absract,
                            url,
                            image_path) 
                            VALUES (?,?,?,?,?,?,?,?) ''',
                             (publisher_id,
                              title,
                              author,
                              release_date,
                              short_abstract,
                              long_abstract,
                              url,
                              image_path))


def find_publisher(db_name, publisher_name):
    with sql.connect(db_name) as con:
        cur = con.cursor().execute('''SELECT publisher_id, name, url FROM publisher WHERE name=:pub_name ''',
                                   {'pub_name': publisher_name})
        row = cur.fetchone()
        if row:
            return {'id': row[0], 'name': row[1], 'url': row[2]}
        else:
            return None


def find_publisher_by_url(db_name, url):
    """Search for a publisher by the URL. The URL may be long and dirty, the function will extract the main part and
    find the publisher, if exists.
    :param db_name:
    :param url: URL like https://www.mann-ivanov-ferber.ru/books/indijskie-mify/.
    The scheme part 'http://' must be present.
    :return: a dictionary with field 'id', 'name', 'url' if the publisher exists, None if not
    """
    url = urlparse.urlparse(url).netloc
    with sql.connect(db_name) as con:
        cur = con.cursor().execute('''SELECT publisher_id, name, url 
                                    FROM publisher 
                                    WHERE instr(url,:pub_url)>0''',
                                   {'pub_url': url})
        row = cur.fetchone()
        if row:
            return {'id': row[0], 'name': row[1], 'url': row[2]}
        else:
            return None


def add_publisher(db_name, name, url=None):
    with sql.connect(db_name) as con:
        con.cursor().execute('''INSERT INTO publisher(name, url) VALUES (?,?) ''', (name, url))


def load_demo(db_name):
    add_publisher(db_name, "МИФ", "www.mann-ivanov-ferber.ru")
    add_publisher(db_name, "Альпина", "https://alpinabook.ru")
    pub_mif = find_publisher(db_name, "МИФ")
    pub_alpina = find_publisher(db_name, "Альпина")
    add_book(db_name, title="Harry Potter", publisher_id=pub_mif['id'], author="J.K. Rowling",
             release_date=dt.datetime.now(),
             short_abstract="Книга о мальчике-волшебнике",
             long_abstract="Мальчик попадает в школу волшебства Хогвартс и учится колдовать")
    add_book(db_name, title="Управление в условиях кризиса: Как выжить и стать сильнее",
             publisher_id=pub_alpina['id'],
             author="Ицхак Адизес",
             release_date=dt.datetime.now(),
             short_abstract='''О том, как руководителям компаний и предпринимателям преодолеть кризис и стать сильнее
    Какие условия диктует кризис и что нужно делать, чтобы он принес пользу
    Написана признанным гуру менеджмента''',
             long_abstract='''Пандемия COVID 19 выявила системные проблемы в организациях, работающих в самых разных сферах. Владельцы бизнесов и топ-менеджмент оказались перед необходимостью срочно перенастраивать ключевые процессы в условиях возросшей неопределенности. Но как пережить кризис и стать сильнее?

Автор теории жизненных циклов компании и типологии руководителей доктор Ицхак Калдерон Адизес последние 50 лет консультирует руководителей крупнейших компаний мира и глав многих государств. Его книга посвящена кризисам и способам извлечения из них пользы.

Кризисы обнажают структурные проблемы в организации, главной из которых доктор Адизес считает отсутствие слаженности, единства, общего видения. Его методика выхода из кризиса через интеграцию частей компании и бизнес-процессов поможет руководителям и предпринимателям сориентироваться в период турбулентности на рынках.''',
             url="https://alpinabook.ru/catalog/book-upravlenie-v-usloviyakh-krizisa-kak-vizhit/")


def list_publishers(db_name):
    with sql.connect(db_name) as con:
        for row in con.cursor().execute('''SELECT * FROM publisher'''):
            print(row)


def list_books(db_name):
    with sql.connect(db_name) as con:
        for row in con.cursor().execute('''SELECT * FROM book'''):
            print(row)


def init_db(db_name=DB_NAME):
    with sql.connect(db_name) as con:
        cur = con.cursor()
        cur.execute('''PRAGMA foreign_keys = ON''')
        cur.execute('''PRAGMA encoding = "UTF-8"''')
        cur.execute('''CREATE TABLE publisher (
                publisher_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                url TEXT)
                ''')
        cur.execute('''CREATE TABLE book ( 
                book_id INTEGER PRIMARY KEY,
                publisher_id INTEGER NOT NULL,
                title TEXT NOT NULL, 
                author TEXT, 
                release_date TEXT, 
                short_abstract TEXT, 
                long_absract TEXT,
                url TEXT,
                image_path TEXT,
                FOREIGN KEY (publisher_id) 
                    REFERENCES publisher (publisher_id)
                )''')


if __name__ == "__main__":
    init_db()
    load_demo(DB_NAME)
    list_publishers(DB_NAME)
    list_books(DB_NAME)
    print(find_publisher_by_url(DB_NAME, "https://www.mann-ivanov-ferber.ru/books/indijskie-mify/"))
    print(find_publisher_by_url(DB_NAME, "https://www.mann-AAivanov-ferber.ru/books/indijskie-mify/"))
