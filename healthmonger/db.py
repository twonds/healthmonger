import itertools
import md5
import time

from whoosh import index, qparser

# healthmonger modules
import config
import memory
import log


def result_tuple(results, offset, limit):
    limit_results = []
    for val in itertools.islice(results, offset, offset+limit):
        limit_results.append(val)
    return len(results), limit_results


class Client:
    """
    """

    def __init__(self, db_type='memory'):
        self.data_loaded = False
        # XXX - memory is only supported right now.
        if db_type == 'memory':
            self.store = memory.Store()
        # Index is used despite the backend we use
        self.index = {}
        for table, schema in config.TABLE_SCHEMA.iteritems():
            # Whoosh used to have a ram index :(
            self.index[table] = index.create_in(config.INDEX_PATH, schema)

    def connect(self):
        """
        """
        return self.store.connect()

    def search(self, table, q, limit=10, offset=0):
        """
        """
        schema = config.TABLE_SCHEMA.get(table)
        pq = qparser.QueryParser('category', schema)
        query = pq.parse(q)
        log.debug(query)
        total, results = self.execute(table, query, limit, offset)
        return total, results

    def search_index(self, table, term):
        """
        """
        results = []
        with self.index[table].searcher() as searcher:
            search_hit = searcher.search(term, limit=None)
            for result in search_hit:
                # We only need the fields, to reference the db
                results.append(result.fields())
        return results

    def execute(self, table, query, limit=25, offset=0):
        """
        """
        results = []
        index_results = self.search_index(table, query)
        for result in index_results:
            for key, value in result.iteritems():
                results.append(self.store.fetch(table, key, value))
        # Grab ids from storage
        return result_tuple(results, offset, limit)

    def load(self, table, table_data):
        if table not in config.TABLE_SCHEMA:
            raise Exception('{0} does not exist'.format(table))
        f = getattr(self, '_handle_'+table)
        if f:
            f(table, table_data)
        else:
            raise Exception('{0} handler does not exist'.format(table))

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
                writer.add_document(id=unicode(row_id),
                                    age_group=unicode(row_tuple[0]),
                                    service=unicode(row_tuple[1]),
                                    gender=unicode(row_tuple[2]),
                                    category=unicode(category),
                                    payer=unicode(row_tuple[3]),
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
