"""
Provides a way to query L{healthmonger} for API information.
Examples, schema, versions, etc.

"""
import random

import config
import log

TXT_EXAMPLE = """
Find documents containing health and care:

http://url.tld/query?table={table}&q=health AND care
Note that AND is the default relation between terms, so this is the same as:

http://url.tld/query?table={table}&q=health care
Find documents containing health, and also either care or modeling:

http://url.tld/query?table={table}&q=health AND care OR modeling
Find documents containing health but not modeling:

http://url.tld/query?table={table}&q=health NOT modeling
Find documents containing alpha but not either beta or gamma:

http://url.tld/query?table={table}&q=alpha NOT (beta OR gamma)
Note that when no boolean operator is specified between terms,
the parser will insert one, by default AND. So this query:

http://url.tld/query?table={table}&q=health care modeling
is equivalent (by default) to:

http://url.tld/query?table={table}&q=health AND care AND modeling
"""


RESPONSE = """
Response:
{'version': %r,
 'result_count': <integer>,
 'results': [<based on table data>]
}
""" % (config.API_VERSION,)


def examples(table):
    """
    Return API examples based on a given table's schema.

    @param table: Table name we want examples for
    @type table: C{string}

    """
    schema = config.TABLE_SCHEMA.get(table)
    if schema is not None:
        response = """{table} API query examples:
{txt}
{keywords}
{ids}
{response}
"""

        txt = ""
        keywords = ""
        ids = ""
        id_list = []
        keyword_list = []

        do_txt = False
        do_ids = False
        do_keywords = False

        for name, item in schema.items():
            log.debug(name)
            item_name = item.__class__.__name__
            if item_name == "ID":
                do_ids = True
                id_list.append(name)
            elif item_name == "KEYWORD":
                do_keywords = True
                keyword_list.append(name)
            elif item_name == "TEXT":
                do_txt = True
            log.debug(item.parse_query)
            log.debug(dir(item))
        if do_ids:
            ids = "ID: "
            ids = ids + ",".join(id_list)
            id = random.choice(id_list)
            ids = ids + """
Example:
http://url.tld/query?table={table}&q={id}:test
""".format(table=table, id=id)
        if do_keywords:
            keywords = "\nKEYWORDS: "
            keywords = keywords + ",".join(keyword_list)
            keyword = random.choice(keyword_list)
            keywords = keywords + """
Example:
http://url.tld/query?table={table}&q={keyword}:test
""".format(table=table, keyword=keyword)
            keyword = random.choice(keyword_list)
            keywords = keywords + """
Example:
http://url.tld/query?table={table}&q={keyword}:test OR {keyword}:65
""".format(table=table, keyword=keyword)

        if do_txt:
            txt = TXT_EXAMPLE.format(table=table)

        return response.format(
            response=RESPONSE,
            table=table,
            txt=txt,
            keywords=keywords,
            ids=ids)
