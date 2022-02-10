import sqlite3
import unittest
import data
import sqlite3 as sql
import os
from os import path
import datetime as dt

# TEST_DB_NAME = "test.db"


class DBTestCase(unittest.TestCase):

    def setUp(self):
        self.test_db_name = f"test_{dt.datetime.now().timestamp()}.db"
        data.init_db(self.test_db_name)

    def tearDown(self):
        os.remove(self.test_db_name)

    def test_init_db(self):
        self.assertTrue(path.exists(self.test_db_name))
        with sql.connect(self.test_db_name) as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM publisher")
            self.assertIsNone(cur.fetchone())
            cur.execute("SELECT * FROM book")
            self.assertIsNone(cur.fetchone())
            cur.execute("SELECT * FROM subscription")
            self.assertIsNone(cur.fetchone())

    def test_find_publisher(self):
        data.load_demo(self.test_db_name)
        mif_pub = data.find_publisher(self.test_db_name, "МИФ")
        self.assertEqual(mif_pub['name'], "МИФ")
        self.assertEqual(mif_pub['url'], "http://mann-ivanov-ferber.ru")
        alpina_pub = data.find_publisher_by_url(self.test_db_name,
                                                "https://alpinabook.ru/some_irrelevant_path?some_parameter")
        self.assertEqual(alpina_pub['name'], "Альпина")
        self.assertEqual(alpina_pub['url'], "http://alpinabook.ru")
        non_exist_pub = data.find_publisher_by_url(self.test_db_name, "https://not-exists.ru")
        self.assertIsNone(non_exist_pub)

    def test_find_books(self):
        MIF_BOOKS_NUM = 1
        ALL_BOOKS_NUM = 3
        INCORRECT_PUB_ID = 1000
        BOOK_TITLE = "Кто мы такие? Гены, наше тело, общество"
        BOOK_AUTHOR = "Роберт Сапольски"
        BOOK_URL = "https://alpinabook.ru/catalog/book-kto-my-takie/"
        INCORRECT_BOOK_URL = "https://alpinabook.ru/catalog/no-such-book"
        FROM_DATE = dt.datetime.fromisoformat("2022-01-25 00:00:00")
        TO_DATE = dt.datetime.fromisoformat("2022-01-27 00:00:00")
        NUM_BOOKS_DATE = 2
        data.load_demo(self.test_db_name)
        mif_pub = data.find_publisher(self.test_db_name, "МИФ")
        alpina_pub = data.find_publisher(self.test_db_name, "Альпина")
        books = data.find_books(self.test_db_name, mif_pub['id'])
        self.assertEqual(len(books), MIF_BOOKS_NUM)
        for b in books:
            self.assertEqual(b['publisher_id'], mif_pub['id'])
        all_books = data.find_books(self.test_db_name)
        self.assertEqual(len(all_books), ALL_BOOKS_NUM)
        empty_books = data.find_books(self.test_db_name, INCORRECT_PUB_ID)
        self.assertEqual(len(empty_books), 0)
        book = data.find_book(self.test_db_name, url=BOOK_URL)
        self.assertEqual(book['publisher_id'], alpina_pub['id'])
        self.assertEqual(book['title'], BOOK_TITLE)
        empty_book = data.find_book(self.test_db_name, url=INCORRECT_BOOK_URL)
        self.assertIsNone(empty_book)
        books = data.find_books(self.test_db_name, from_date=FROM_DATE,
                                to_date=TO_DATE)
        self.assertEqual(len(books), NUM_BOOKS_DATE)
        books = data.find_books(self.test_db_name, author=BOOK_AUTHOR, from_date=FROM_DATE,
                                to_date=TO_DATE)
        self.assertEqual(len(books), 1)

    def test_add_book(self):
        BOOK_TITLE = "New book"
        BOOK_AUTHOR = "Some Guy"
        BOOK_URL = "http://some-url.ru/book-page/"
        data.load_demo(self.test_db_name)
        mif_pub = data.find_publisher(self.test_db_name, "МИФ")
        num_books = len(data.find_books(self.test_db_name))
        num_mif_books = len(data.find_books(self.test_db_name, publisher_id=mif_pub['id']))
        data.add_book(self.test_db_name, title=BOOK_TITLE, author=BOOK_AUTHOR, publisher_id=mif_pub['id'],
                      url=BOOK_URL)
        self.assertEqual(num_books+1, len(data.find_books(self.test_db_name)))
        self.assertEqual(num_mif_books + 1, len(data.find_books(self.test_db_name, publisher_id=mif_pub['id'])))
        book = data.find_book(self.test_db_name, url=BOOK_URL)
        self.assertEqual(book['publisher_id'], mif_pub['id'])
        self.assertEqual(book['title'], BOOK_TITLE)
        self.assertEqual(book['author'], BOOK_AUTHOR)
        # test duplicate url
        self.assertRaises(sql.DatabaseError, data.add_book, *[self.test_db_name, BOOK_TITLE, mif_pub['id']],
                          **{'author': BOOK_AUTHOR, 'url': BOOK_URL})

    def test_add_subscription(self):
        data.load_demo(self.test_db_name)
        publisher_name = data.get_all_publishers(self.test_db_name).fetchone()['name']
        test_user_id = 123456
        data.add_subscription(self.test_db_name, test_user_id, publisher_name, "0 10 * * 1")
        cur = sqlite3.connect(self.test_db_name).cursor().execute("SELECT * FROM subscription")
        self.assertIsNotNone(cur.fetchone())


if __name__ == '__main__':
    unittest.main()
