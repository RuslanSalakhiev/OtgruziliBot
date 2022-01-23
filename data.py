import sqlite3 as sql
import datetime as dt


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
        return {'id': row[0], 'name': row[1], 'url': row[2]}


def add_publisher(db_name, name, url=None):
    with sql.connect(db_name) as con:
        con.cursor().execute('''INSERT INTO publisher(name, url) VALUES (?,?) ''', (name, url))


def load_demo(db_name):
    add_publisher(db_name, "Magic Publishing", "www.heaven-pub.com")
    add_publisher(db_name, "Boring Ltd.", "www.hell.com")
    pub_magic = find_publisher(db_name, "Magic Publishing")
    pub_boring = find_publisher(db_name, "Boring Ltd.")
    add_book(db_name, title="Harry Potter", publisher_id=pub_magic['id'], author="J.K. Rowling",
             release_date=dt.datetime.now(),
             short_abstract="Книга о мальчике-волшебнике",
             long_abstract="Мальчик попадает в школу волшебства Хогвартс и учится колдовать")
    add_book(db_name, title="1000 секретов Excel", publisher_id=pub_boring['id'], author="С.К. Иванов",
             release_date=dt.datetime.now(),
             short_abstract="Все про Excel")


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
    load_demo(db_name)


if __name__ == "__main__":
    init_db()
    list_publishers(DB_NAME)
    list_books(DB_NAME)
