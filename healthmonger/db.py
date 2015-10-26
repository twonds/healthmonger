import itertools
import md5
import time

from operator import le, ge, eq, lt, gt, itemgetter
from whoosh import index

# healthmonger modules
import config
import memory
import log
import query

COMPARISON_OPERATORS = {
    '<=': le,
    '>=': ge,
    '=': eq,
    '<': lt,
    '>': gt,
}

# XXX - move this to config or specific to age and gender
FULLTEXT_KEYS = ('age', 'group', 'service', 'payer')


def search_op(op, terms):
    terms = filter(None, terms)
    if not terms:
        return terms
    elif len(terms) == 1:
        return terms[0]
    else:
        return op(terms)


def result_tuple(results, offset, limit):
    limit_results = []
    for val in itertools.islice(results, offset, offset+limit):
        limit_results.append(val[0])
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
            self.index[table] = index.create_in(config.INDEX_PATH, schema)

    def connect(self):
        """
        """
        return self.store.connect()

    def search(self, table, q, limit=10, offset=None):
        """
        """
        pq = query.SearchQueryParser().parse(q)
        total, results = self.execute(table, pq, limit, offset)
        return total, results

    def parse_fulltext_query(self, table, keys, val):
        """
        """
        schema = self.index[table].schema
        val = unicode(val)
        if not val.strip():
            return []

        def terms(key):
            tokens = schema[key].process_text(
                val, mode='query', tokenize=True, removestops=True)
            return [query.Term(key, token) for token in tokens]

        return search_op(
            query.Or,
            [search_op(query.And, terms(key)) for key in keys])

    def search_index(self, table, term):
        """
        """
        with self.index[table].searcher() as searcher:
            results = searcher.search(term, limit=None)
            return ((g['id'], g['timestamp']) for g in results)

    def execute(self, table, query_op, limit=25, offset=0):
        """
        """
        def _do_op(query_op):
            log.debug(query_op)
            if query_op is None:
                # XXX - need data API!
                result = self.store.data[table]
            elif isinstance(query_op, query.And):
                left, right = query_op.arguments
                result = _do_op(left).intersection(_do_op(right))
            elif isinstance(query_op, query.Or):
                left, right = query_op.arguments
                result = _do_op(left).union(_do_op(right))
            elif isinstance(query_op, query.Not):
                # XXX - store needs data fetch API
                diff_ops = _do_op(query_op.arguments[0])
                result = self.store.data[table].difference(diff_ops)
            elif isinstance(query_op, query.Literal):
                arg = query_op.arguments[0].lower()
                prefix, _, val = arg.partition(':')
                log.debug(prefix)
                log.debug(val)
                if prefix in FULLTEXT_KEYS or prefix == 'search':
                    if prefix == 'search':
                        keys = FULLTEXT_KEYS
                    else:
                        keys = [prefix]
                    term = self.parse_fulltext_query(table, keys, val)
                    if term:
                        result = set(self.search_index(table, term))
                    else:
                        # XXX - API me!
                        result = self.store.data[table]
                else:
                    log.debug(arg)
                    # XXX - API please!
                    log.debug('The literal is not in the index?')
                    result = self.store.data[table][arg]
            elif isinstance(query_op, query.Numerical):
                op = COMPARISON_OPERATORS[query_op.arguments[1]]
                key = query_op.arguments[0]
                const = query_op.arguments[2]
                tmp = []
                for k, val, timestamp in self.store[table][key]:
                    if op(val, const):
                        tmp.append((k, timestamp))
                result = set(tmp)
            else:
                result = set()
            return result

        op_result = sorted(_do_op(query_op), key=itemgetter(1), reverse=True)
        return result_tuple(op_result, offset, limit)

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
        writer = self.index['age_and_gender'].writer()
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
                store[row_id].add(row_tuple)
                # store[row_tuple].add(row_tuple)
                store[category].add(row_tuple)
                writer.add_document(age_group=unicode(row_tuple[0]),
                                    service=unicode(row_tuple[1]),
                                    gender=unicode(row_tuple[2]),
                                    category=unicode(category),
                                    payer=unicode(row_tuple[3]))
        self.store.update_store(table_name, store, ts)
        writer.commit()
