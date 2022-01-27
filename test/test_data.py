import unittest
import data
import sqlite3 as sql
import os
from os import path

TEST_DB_NAME = "test.db"


class DBTestCase(unittest.TestCase):

    def setUp(self):
        data.init_db(TEST_DB_NAME)

    def tearDown(self):
        os.remove(TEST_DB_NAME)

    def test_init_db(self):
        self.assertTrue(path.exists(TEST_DB_NAME))
        with sql.connect(TEST_DB_NAME) as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM publisher")
            self.assertIsNone(cur.fetchone())
            cur.execute("SELECT * FROM book")
            self.assertIsNone(cur.fetchone())

    def test_find_publisher(self):
        data.load_demo(TEST_DB_NAME)
        mif_pub = data.find_publisher(TEST_DB_NAME, "МИФ")
        self.assertEqual(mif_pub['name'], "МИФ")
        self.assertEqual(mif_pub['url'], "http://mann-ivanov-ferber.ru")
        alpina_pub = data.find_publisher_by_url(TEST_DB_NAME,
                                                "https://alpinabook.ru/some_irrelevant_path?some_parameter")
        self.assertEqual(alpina_pub['name'], "Альпина")
        self.assertEqual(alpina_pub['url'], "http://alpinabook.ru")
        non_exist_pub = data.find_publisher_by_url(TEST_DB_NAME, "https://not-exists.ru")
        self.assertIsNone(non_exist_pub)

    def test_find_books(self):
        MIF_BOOKS_NUM = 1
        ALL_BOOKS_NUM = 3
        INCORRECT_PUB_ID = 1000
        BOOK_URL = "https://alpinabook.ru/catalog/book-kto-my-takie/"
        INCORRECT_BOOK_URL = "https://alpinabook.ru/catalog/no-such-book"
        data.load_demo(TEST_DB_NAME)
        mif_pub = data.find_publisher(TEST_DB_NAME, "МИФ")
        alpina_pub = data.find_publisher(TEST_DB_NAME, "Альпина")
        books = data.find_books(TEST_DB_NAME, mif_pub['id'])
        self.assertEqual(len(books), MIF_BOOKS_NUM)
        for b in books:
            self.assertEqual(b['publisher_id'], mif_pub['id'])
        all_books = data.find_books(TEST_DB_NAME)
        self.assertEqual(len(all_books), ALL_BOOKS_NUM)
        empty_books = data.find_books(TEST_DB_NAME, INCORRECT_PUB_ID)
        self.assertEqual(len(empty_books), 0)
        book = data.find_book(TEST_DB_NAME, url=BOOK_URL)
        self.assertEqual(book['publisher_id'], alpina_pub['id'])
        self.assertEqual(book['title'], "Кто мы такие? Гены, наше тело, общество")
        empty_book = data.find_book(TEST_DB_NAME, url=INCORRECT_BOOK_URL)
        self.assertIsNone(empty_book)

    def test_add_book(self):
        BOOK_TITLE = "New book"
        BOOK_AUTHOR = "Some Guy"
        BOOK_URL = "http://some-url.ru/book-page/"
        data.load_demo(TEST_DB_NAME)
        mif_pub = data.find_publisher(TEST_DB_NAME, "МИФ")
        num_books = len(data.find_books(TEST_DB_NAME))
        num_mif_books = len(data.find_books(TEST_DB_NAME, publisher_id=mif_pub['id']))
        data.add_book(TEST_DB_NAME, title=BOOK_TITLE, author=BOOK_AUTHOR, publisher_id=mif_pub['id'],
                      url=BOOK_URL)
        self.assertEqual(num_books+1, len(data.find_books(TEST_DB_NAME)))
        self.assertEqual(num_mif_books + 1, len(data.find_books(TEST_DB_NAME, publisher_id=mif_pub['id'])))
        book = data.find_book(TEST_DB_NAME, url=BOOK_URL)
        self.assertEqual(book['publisher_id'], mif_pub['id'])
        self.assertEqual(book['title'], BOOK_TITLE)
        self.assertEqual(book['author'], BOOK_AUTHOR)
        # test duplicate url
        self.assertRaises(sql.DatabaseError, data.add_book, *[TEST_DB_NAME, BOOK_TITLE, mif_pub['id']],
                          **{'author': BOOK_AUTHOR, 'url': BOOK_URL})


if __name__ == '__main__':
    unittest.main()
