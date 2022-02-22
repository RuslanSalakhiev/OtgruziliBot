import sqlite3 as sql
import datetime as dt
import urllib.parse as urlparse
import config
import argparse
from collections import namedtuple

Book = namedtuple('Book',
                  ['book_id', 'publisher_id', 'title', 'author',
                   'release_date', 'short_abstract', 'long_absract', 'url', 'image_path','is_sent_to_channel'])

def get_args():
    parser = argparse.ArgumentParser(description="The module creates and manages the database for OtgruziliBot. \
                                    Usage: \n \
                                        python data.py db_name")
    parser.add_argument("--loaddemo", action="store_true", help="Load demo data into the created database")
    parser.add_argument("--upgrade", action="store_true", help="Creates subscription table for the given database")
    parser.add_argument("db_name", help="The path to the database")
    return parser.parse_args()


def add_book(db_name, title, publisher_id, author=None, release_date=None,
             short_abstract=None, long_abstract=None,
             url=None,
             image_path=None):
    if not release_date:
        release_date = dt.datetime.now()
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


def find_books(db_name, publisher_id=None,
               title=None, author=None,
               from_date=None, to_date=None):
    """Returns all book which meets the given parameters.
    If all parameters are None, all books in the database are returned.
    :param db_name:
    :param publisher_id:
    :param title:
    :param author:
    :param from_date: the condition is from_date<=release_date<to_date
    :param to_date:
    :return: a sequence of sqlite3.Row dict-like entries
    """
    def build_query():
        query = "SELECT * FROM book"
        vals = build_values()
        if vals:
            query += " WHERE"
            parts = [f" {k}=:{k}" for k in vals if k not in {'from_date', 'to_date'}]
            parts += [" release_date>=:from_date"] if from_date else []
            parts += [" release_date<:to_date"] if to_date else []
            query += " AND".join(parts)
        return query

    def build_values():
        val = {'publisher_id': publisher_id, 'title': title, 'author': author,
               'from_date': from_date, 'to_date': to_date}
        return dict({(k, v) for k, v in val.items() if v})

    with sql.connect(db_name) as con:
        con.row_factory = sql.Row
        cur = con.cursor()
        q = build_query()
        v = build_values()
        cur.execute(q, v)
        return [b._asdict() for b in map(Book._make, cur.fetchall())]


def find_book(db_name, url):
    with sql.connect(db_name) as con:
        con.row_factory = sql.Row
        cur = con.cursor()
        cur.execute("SELECT * FROM book WHERE book.url=:book_url", {'book_url': url})
        return cur.fetchone()


def _row_to_publisher(row):
    return {'id': row[0], 'name': row[1], 'url': row[2]}

def find_publisher(db_name, publisher_name):
    with sql.connect(db_name) as con:
        cur = con.cursor().execute('''SELECT publisher_id, name, url FROM publisher WHERE name=:pub_name ''',
                                   {'pub_name': publisher_name})
        row = cur.fetchone()
        if row:
            return _row_to_publisher(row)
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
            return _row_to_publisher(row)
        else:
            return None


def add_publisher(db_name, name, url=None):
    with sql.connect(db_name) as con:
        con.cursor().execute('''INSERT INTO publisher(name, url) VALUES (?,?) ''', (name, url))


def load_demo(db_name):
    add_publisher(db_name, "МИФ", "http://mann-ivanov-ferber.ru")
    add_publisher(db_name, "Альпина", "http://alpinabook.ru")
    pub_mif = find_publisher(db_name, "МИФ")
    pub_alpina = find_publisher(db_name, "Альпина")
    add_book(db_name, title="Harry Potter", publisher_id=pub_mif['id'], author="J.K. Rowling",
             release_date=dt.datetime.fromisoformat("2022-01-25 12:10:45"),
             short_abstract="Книга о мальчике-волшебнике",
             long_abstract="Мальчик попадает в школу волшебства Хогвартс и учится колдовать")
    add_book(db_name, title="Управление в условиях кризиса: Как выжить и стать сильнее",
             publisher_id=pub_alpina['id'],
             author="Ицхак Адизес",
             release_date=dt.datetime.fromisoformat("2022-01-27 18:30:00"),
             short_abstract='''О том, как руководителям компаний и предпринимателям преодолеть кризис и стать сильнее
    Какие условия диктует кризис и что нужно делать, чтобы он принес пользу
    Написана признанным гуру менеджмента''',
             long_abstract='''Пандемия COVID 19 выявила системные проблемы в организациях, работающих в самых разных сферах. Владельцы бизнесов и топ-менеджмент оказались перед необходимостью срочно перенастраивать ключевые процессы в условиях возросшей неопределенности. Но как пережить кризис и стать сильнее?

Автор теории жизненных циклов компании и типологии руководителей доктор Ицхак Калдерон Адизес последние 50 лет консультирует руководителей крупнейших компаний мира и глав многих государств. Его книга посвящена кризисам и способам извлечения из них пользы.

Кризисы обнажают структурные проблемы в организации, главной из которых доктор Адизес считает отсутствие слаженности, единства, общего видения. Его методика выхода из кризиса через интеграцию частей компании и бизнес-процессов поможет руководителям и предпринимателям сориентироваться в период турбулентности на рынках.''',
             url="https://alpinabook.ru/catalog/book-upravlenie-v-usloviyakh-krizisa-kak-vizhit/")
    add_book(db_name, title="Кто мы такие? Гены, наше тело, общество",
             publisher_id=pub_alpina['id'],
             author="Роберт Сапольски",
             release_date=dt.datetime.fromisoformat("2022-01-26 08:35:16"),
             short_abstract="",
             long_abstract="",
             url="https://alpinabook.ru/catalog/book-kto-my-takie/"
             )


def print_publishers(db_name):
    with sql.connect(db_name) as con:
        for row in con.cursor().execute('''SELECT * FROM publisher'''):
            print(row)


def get_all_publishers(db_name):
    with sql.connect(db_name) as con:
        con.row_factory = sql.Row
        return [_row_to_publisher(row) for row in con.cursor().execute('''SELECT * FROM publisher''').fetchall()]


def print_books(db_name):
    with sql.connect(db_name) as con:
        for row in con.cursor().execute('''SELECT * FROM book'''):
            print(row)


def add_subscription(db_name, tg_user_id, publisher_name, cron_str):
    pub_id = find_publisher(db_name, publisher_name)['id']
    with sql.connect(db_name) as con:
        con.cursor().execute('''INSERT OR REPLACE INTO 
                            subscription(tg_user_id, publisher_id, cron_str)
                            VALUES(:tgid, :pub_id, :str)
                            ''',
                             {'tgid': tg_user_id,
                              'pub_id': pub_id,
                              'str': cron_str})


def create_tbl_subscription(db_name):
    with sql.connect(db_name) as con:
        # cron_str is like:
        # minute hour day_of_month month day_of_week
        # https://crontab.guru/
        con.cursor().execute('''CREATE TABLE IF NOT EXISTS subscription (
                            tg_user_id INTEGER NOT NULL,
                            publisher_id INTEGER NOT NULL,
                            cron_str TEXT NOT NULL, 
                            FOREIGN KEY (publisher_id) 
                                REFERENCES publisher (publisher_id),
                            PRIMARY KEY (tg_user_id, publisher_id))''')


def init_db(db_name):
    with sql.connect(db_name) as con:
        cur = con.cursor()
        cur.execute('''PRAGMA foreign_keys = ON''')
        cur.execute('''PRAGMA encoding = "UTF-8"''')
        cur.execute('''CREATE TABLE IF NOT EXISTS publisher (
                publisher_id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE,
                url TEXT)
                ''')
        cur.execute('''CREATE TABLE IF NOT EXISTS book ( 
                book_id INTEGER PRIMARY KEY,
                publisher_id INTEGER NOT NULL,
                title TEXT NOT NULL, 
                author TEXT, 
                release_date TEXT, 
                short_abstract TEXT, 
                long_absract TEXT,
                url TEXT UNIQUE,
                image_path TEXT,
                is_sent_to_channel INTEGER DEFAULT 0,
                FOREIGN KEY (publisher_id) 
                    REFERENCES publisher (publisher_id)
                )''')
    create_tbl_subscription(db_name)


if __name__ == "__main__":
    args = get_args()
    if args.upgrade:
        create_tbl_subscription(args.db_name)
        print(f"Subscription table was created for the database {args.db_name}")
    else:
        init_db(args.db_name)
        print(f"Database was created at {args.db_name}")
    if args.loaddemo:
        load_demo(args.db_name)
        print("Demo data is loaded:")
        print(f"{get_all_publishers(args.db_name)} publishers, {find_books(args.db_name)} books")

    # print_publishers(config.db_name)
    # print_books(config.db_name)
    # print(find_publisher_by_url(config.db_name, "https://www.mann-ivanov-ferber.ru/books/indijskie-mify/"))
    # print(find_publisher_by_url(config.db_name, "https://www.mann-AAivanov-ferber.ru/books/indijskie-mify/"))
