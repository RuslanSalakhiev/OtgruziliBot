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
        ALL_BOOKS_NUM = 2
        INCORRECT_PUB_ID = 1000
        data.load_demo(TEST_DB_NAME)
        mif_pub = data.find_publisher(TEST_DB_NAME, "МИФ")
        books = data.find_books(TEST_DB_NAME, mif_pub['id'])
        self.assertEqual(len(books), MIF_BOOKS_NUM)
        for b in books:
            self.assertEqual(b['publisher_id'], mif_pub['id'])
        all_books = data.find_books(TEST_DB_NAME)
        self.assertEqual(len(all_books), ALL_BOOKS_NUM)
        empty_books = data.find_books(TEST_DB_NAME, INCORRECT_PUB_ID)
        self.assertEqual(len(empty_books), 0)


if __name__ == '__main__':
    unittest.main()
