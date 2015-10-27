"""
This module provides search index and database access for L{healthmonger}.
"""
import itertools
import md5
import os
import time

from whoosh import index, qparser

# healthmonger modules
import config
import memory
import log


def result_tuple(results, offset, limit):
    """
    Limit a set of results be the given offset and limit.

    @param results: The total list of results.
    @type results: C{list}

    @param offset: The offset used to return a subset of results
    @type offset: C{int}

    @param limit: The number of results expected.
    @type limit: C{int}

    @return: The total number of results along with results sliced
             by offset and limit.
    @rtype: C{tuple} of (C{int}, C{list})
    """
    limit_results = []
    for val in itertools.islice(results, offset, offset+limit):
        limit_results.append(val)
    return len(results), limit_results


class InvalidTable(Exception):
    """
    An exception raised when accessing an unknow or invalid database table.
    """
    pass


class Client:
    """
    API for accessing the search index and datastores.

    Search index is a L{Whoosh} index

    @note: Supported databases: L{healthmonger.memory}
    """

    def __init__(self, db_type='memory'):
        """
        Setup a client that contains a search index and client to a database.

        @param db_type: The database type to use.
        @type db_type: C{string}

        """
        self.data_loaded = False
        # XXX - memory is only supported right now.
        if db_type == 'memory':
            self.store = memory.Store()
        # Index is used despite the backend we use
        self.index = {}
        for table, schema in config.TABLE_SCHEMA.iteritems():
            path = config.INDEX_PATH+"/"+table
            if not os.path.exists(path):
                os.makedirs(path)
            # Whoosh used to have a ram index :(
            self.index[table] = index.create_in(config.INDEX_PATH, schema)

    def connect(self):
        """
        Connect to the backend storage.
        """
        return self.store.connect()

    def search(self, table, q, limit=10, offset=0, **kwargs):
        """
        Search the index with the given query string and fetch found
        results from the database.

        @param table: Table name to search
        @type table: C{string}

        @param q: Query string for the index. Example: this OR that
        @type  q: C{string}

        @param limit: Limit the number of results returned by the search.
        @type limit: C{int}

        @param offset: Used to indicate the position to start returning
                       data from.
        @type offset: C{int}

        @note: The rest of the key word arguments are passed along and used
               if there is a filter handler defined for the table.
        """
        schema = config.TABLE_SCHEMA.get(table)
        # XXX - need a default field to search against
        pq = qparser.QueryParser('category', schema)
        query = pq.parse(q)
        try:
            total, results = self.execute(table, query,
                                          limit, offset, **kwargs)
        except KeyError:
            raise InvalidTable(table)
        return total, results

    def search_index(self, table, term, limit=25, offset=0):
        """
        Search the index returning the hit results with references
        to data in storage.

        @param table: The table name to search.
        @type table: C{string}

        @param term: Parsed query term used by the index searcher.
        @type term: C{string}

        @param limit: Limit the number of results returned by the search.
        @type limit: C{int}

        @param offset: Used to indicate the position to start returning data
                       from.
        @type offset: C{int}
        """
        results = []
        with self.index[table].searcher() as searcher:
            search_hit = searcher.search_page(term, offset+1, limit)
            for result in search_hit:
                # We only need the fields to query the db
                results.append(result.fields())
        return results

    def execute(self, table, query, limit=25, offset=0, **kwargs):
        """
        Execute a request by searching the index via a parsed query string.
        Then retrieve the data from the datastore and filter based on table
        and arguments given.

        @param table: The table name to search.
        @type table: C{string}

        @param query: Query string for searching the database.
        @type query: C{string}

        @param limit: Limit the number of results returned by the search.
        @type limit: C{int}

        @param offset: Used to indicate the position to start returning
                       data from.
        @type offset: C{int}

        @note: The rest of the key word arguments are passed along and used
               if there is a filter handler defined for the table.
        """
        results = []
        index_results = self.search_index(table, query,
                                          limit=limit,
                                          offset=offset)
        for result in index_results:
            for key, value in result.iteritems():
                results.append(self.store.fetch(table, key, value))
        f = getattr(self, "_filter_"+table, None)
        if f is not None:
            result = f(table, results, offset, limit, **kwargs)
        else:
            result = result_tuple(results, offset, limit)

        return result

    def load(self, table, table_data):
        """
        Load data into the index and datastore.

        @param table: Table name to load data into. A schema in the
                      configuration matching the table MUST exist.
        @type table: C{string}

        @param table_data: Data to load into the table. The type of this data
                           is specific to the data loader handlers.
        """
        if table not in config.TABLE_SCHEMA:
            raise Exception('{0} does not exist'.format(table))
        f = getattr(self, '_handle_'+table)
        if f:
            f(table, table_data)
        else:
            raise Exception('{0} handler does not exist'.format(table))

    def _filter_age_and_gender(self, table, results, offset, limit, **kwargs):
        return_filter = kwargs.get('filter', 'years')
        if return_filter is None:
            return_filter = 'years'
        return_filter = return_filter.split()
        new_results = []
        log.debug(kwargs)
        log.debug(return_filter)
        if return_filter != ['years']:
            for result in results:
                log.debug(result)
                log.debug(return_filter)
                for year in ['2002', '2004', '2006', '2008', '2010']:
                    if year not in return_filter:
                        del result[year]
                new_results.append(result)
            results = new_results
        return result_tuple(results, offset, limit)

    def _age_and_gender_tuple(self, row, category, ts):
        row_id = None
        age_group = row.get('Age Group', '')
        service = row.get('Service', '')
        gender = row.get('Gender', '')
        payer = row.get('Payer', '')
        year_2002 = row.get('2002', '')
        year_2004 = row.get('2004', '')
        year_2006 = row.get('2006', '')
        year_2008 = row.get('2008', '')
        year_2010 = row.get('2010', '')
        m = md5.new(age_group+service+gender+payer)
        row_id = m.hexdigest()
        return (row_id, (age_group, service, gender, payer,
                         year_2002, year_2004, year_2006,
                         year_2008, year_2010, category, ts))

    def _handle_age_and_gender(self, table_name, table_data):
        """Handles data for the age and gender health expenditure table.
        """
        writer = self.index[table_name].writer()
        # New store is a temporary store.
        # When a commit occures it will then overwrite the old.
        store = self.store.new_store()
        for name, data in table_data.iteritems():
            log.debug(name)
            # XXX - should parse this better
            category = " ".join(name[:-4].split()[3:])
            ts = time.time()
            log.debug(category)
            for row in data:
                row_id, row_tuple = self._age_and_gender_tuple(row,
                                                               category,
                                                               ts)
                store[u'id:'+unicode(row_id)] = row
                store[category].add(row_id)
                # Store this both lower and raw
                writer.add_document(id=unicode(row_id),
                                    age_group=unicode(row_tuple[0]),
                                    service=unicode(row_tuple[1]),
                                    gender=unicode(row_tuple[2]),
                                    category=unicode(category),
                                    payer=unicode(row_tuple[3]),
                                    timestamp=unicode(ts))
                writer.add_document(id=unicode(row_id),
                                    age_group=unicode(row_tuple[0].lower()),
                                    service=unicode(row_tuple[1].lower()),
                                    gender=unicode(row_tuple[2].lower()),
                                    category=unicode(category.lower()),
                                    payer=unicode(row_tuple[3].lower()),
                                    timestamp=unicode(ts))
        self.store.update_store(table_name, store, ts)
        writer.commit()

    def _handle_unittest(self, table_name, table_data):
        """Only used to load unittest data
        """
        writer = self.index[table_name].writer()
        store = self.store.new_store()
        for data in table_data:
            store[u'id:'+unicode(data['id'])] = data
            writer.add_document(id=unicode(data.get('id')),
                                category=unicode(data.get('category')),
                                content=unicode(data.get('content')),
                                timestamp=unicode(data.get('timestamp')))
        writer.commit()
        self.store.update_store(table_name, store, data.get('timestamp'))
