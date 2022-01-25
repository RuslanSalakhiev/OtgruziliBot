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


if __name__ == '__main__':
    unittest.main()
