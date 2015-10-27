import time
import unittest

from whoosh import fields

from healthmonger import config
from healthmonger import db as healthmonger_db

TABLE_NAME = 'unittest'

TEST_DATA = [{'id': 1,
              'category': 'wat',
              'content': 'test wat',
              'timestamp': time.time()},
             {'id': 2,
              'category': 'new',
              'content': 'the first test',
              'timestamp': time.time()}]


class TestConfig:
    INDEX_PATH = config.INDEX_PATH
    TABLE_SCHEMA = {TABLE_NAME: fields.Schema(id=fields.ID(stored=True),
                                              category=fields.KEYWORD,
                                              content=fields.TEXT,
                                              timestamp=fields.ID)}


class Db(unittest.TestCase):

    def setUp(self):
        # fake the configuration
        self._test_config = healthmonger_db.config
        healthmonger_db.config = TestConfig()

    def tearDown(self):
        healthmonger_db.config = self._test_config

    def test_basic(self):
        db = healthmonger_db.Client()
        self.assertEqual(None, db.connect())
        assert(TABLE_NAME in db.index)

    def test_load(self):
        db = healthmonger_db.Client()
        db.load(TABLE_NAME, TEST_DATA)
        self.assertEqual(True, TABLE_NAME in db.store.data.keys())

    def test_category_query(self):
        db = healthmonger_db.Client()
        db.load(TABLE_NAME, TEST_DATA)
        total, results = db.search(TABLE_NAME, 'wat')
        self.assertEqual(1, total)
        expected_data = TEST_DATA[0]
        for key, value in expected_data.iteritems():
            self.assertEqual(value, results[0].get(key))

    def test_basic_query(self):
        db = healthmonger_db.Client()
        db.load(TABLE_NAME, TEST_DATA)
        total, results = db.search(TABLE_NAME, 'content:test')
        self.assertEqual(2, total)
        expected_data = TEST_DATA[0]
        for key, value in expected_data.iteritems():
            self.assertEqual(value, results[0].get(key))

    def test_or_query(self):
        db = healthmonger_db.Client()
        db.load(TABLE_NAME, TEST_DATA)
        total, results = db.search(TABLE_NAME, 'wat OR new')
        self.assertEqual(2, total)
        expected_data = TEST_DATA[0]
        for key, value in expected_data.iteritems():
            self.assertEqual(value, results[0].get(key))
