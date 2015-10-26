"""In memory data store
"""
from collections import defaultdict

import config


class Store:
    """
    """

    def __init__(self):
        self.data_loaded = False
        self.time_loaded = None
        self.data = {}
        for table, schema in config.TABLE_SCHEMA.iteritems():
            self.data[table] = self.new_store()

    def new_store(self):
        return defaultdict(set)

    def update_store(self, table, store, timestamp):
        self.data[table] = store
        self.time_loaded = timestamp
        self.data_loaded = True

    def connect(self):
        """This connects to nothing since this is in memory.
        Used to do some initialization.
        """
