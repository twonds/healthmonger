"""In memory data store module
"""
from collections import defaultdict

import config


class Store:
    """Simple in-memory data store.
    """

    def __init__(self):
        self.data_loaded = False
        self.time_loaded = None
        self.data = defaultdict(dict)
        for table, schema in config.TABLE_SCHEMA.iteritems():
            self.data[table] = self.new_store()

    def new_store(self):
        """
        Create and return an new storage type.
        """
        return defaultdict(set)

    def update_store(self, table, store, timestamp):
        """Update a table with new data. This overwrites the old data.

        @param table: Table name
        @type table: C{string}

        @param store: The new table data that will replace the old
        @param store: C{dict}

        @param timestamp: The timestamp to mark the time this data was loaded
        @type timestamp: C{int}
        """
        self.data[table] = store
        self.time_loaded = timestamp
        self.data_loaded = True

    def connect(self):
        """
        This connects to nothing since this is in memory.
        Used to do some initialization.
        """

    def insert(self, table_name, key, value, obj):
        """Insert a row of data into the table keyed by a key and value.
        This is used for quick lookups when hits from a search index are
        a key and value in the row.

        @param table_name: The name of the table
        @type table_name: C{string}

        @param key: The key indicating where the data is located.
        @type key: any

        @param value: The value stored in that key. The key and value are
                      used to create a lookup key for the entire row
        @type value: any

        @parm obj: The row of data we want to store
        @type obj: any
        """
        i = unicode(key)+u':'+unicode(value)
        self.data[table_name][i] = obj

    def fetch(self, table_name, key, value):
        """Fetch a row or object based on a key and value in that row.
        @param table_name: The name of the table
        @type table_name: C{string}

        @param key: The key indicating where the data is located.
        @type key: any

        @param value: The value stored in that key. The key and value are
                      used to create a lookup key for the entire row
        @type value: any
        """
        i = unicode(key)+u':'+unicode(value)
        return self.data[table_name][i]
