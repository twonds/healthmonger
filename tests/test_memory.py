import copy
import unittest

from healthmonger import memory


class Memory(unittest.TestCase):
    """Ensure memory storage API is accesible and works.
    """

    def test_basic(self):
        m = memory.Store()
        self.assertEqual(False, m.data_loaded)
        self.assertEqual(None, m.time_loaded)
        assert(len(m.data.keys()) > 0)

    def test_connect(self):
        m = memory.Store()
        # Just need the api method
        self.assertEqual(None, m.connect())

    def test_new_store(self):
        m = memory.Store()
        # Configuration MUST have one table schema
        table = m.data.keys()[0]
        self.assertEqual(m.data[table], m.new_store())

    def test_update_store(self):
        m = memory.Store()
        store = m.new_store()
        table = m.data.keys()[0]
        old_store = copy.deepcopy(m.data[table])
        store['test'] = 'new data'
        m.update_store(table, store, 1234)
        self.assertEqual(m.data[table], store)
        self.assertNotEqual(old_store, m.data[table])

    def test_fetch(self):
        value = {'id': 1, 'wat': 'wat'}
        m = memory.Store()
        m.insert('test', 'id', 1, value)
        result = m.fetch('test', 'id', 1)
        for key, value in value.iteritems():
            self.assertEqual(value, result.get(key))
