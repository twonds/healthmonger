"""
L{healthmonger}'s main flask application providing the HTTP JSON API.
"""
import flask

# healthmonger modules
import config
import disco
import db
import loader
import log

app = flask.Flask(__name__)
app.debug = config.debug
app.config.from_object(config)

db_client = db.Client()


@app.route('/')
def index():
    """
    Return a list of tables and their corresponding API examples.
    """
    response = ""
    for table in config.TABLE_SCHEMA.keys():
        response = response + disco.examples(table)
    return response


@app.route('/load')
def load_data():
    """
    Load all table data into the search index.
    """
    try:
        loader.download()
        load_table_data()
        status = 'loaded'
    except Exception as ex:
        log.log_traceback(ex)
        status = 'failed'
    return flask.jsonify({'status': status})


@app.route('/status')
def status():
    """
    Report if the status of the service is OK or NOT_OK. If the service is OK
    then the API is available.
    """
    response = "NOT_OK"
    if db_client.data_loaded:
        response = "OK"
    return flask.jsonify({'status': response})


@app.route('/disco')
def discovery():
    """
    Discover information about the tables on this API endpoint.
    """
    table = flask.request.args.get('table')
    response = 'Invalid table:'+str(table)
    status = 404
    response = disco.examples(table)
    if response:
        status = 200
    return flask.Response(response, status=status)


@app.route('/query')
def query():
    """
    Query healthcare data stored in L{healthmonger}
    """
    data = {'version': config.API_VERSION}
    args = flask.request.args
    limit = args.get('limit', config.DEFAULT_QUERY_LIMIT)
    offset = args.get('offset', 0)
    q = args.get('q', '')
    table = args.get('table')
    filter_params = {'filter': args.get('filter')}
    try:
        total, result = db_client.search(table, q,
                                         limit, offset,
                                         **filter_params)
        data['result_count'] = total
        data['results'] = result
    except db.InvalidTable:
        data['error'] = 'Invalid table:'+str(table)

    return flask.jsonify(data)


def load_table_data():
    log.debug("Loading table data...")
    for table, data in loader.read():
        log.debug(table)
        db_client.load(table, data)
    db_client.data_loaded = True


if __name__ == '__main__':
    log.debug("Starting ...")
    db_client.connect()
    # Download data if we do not have it.
    loader.download(exists=False)
    load_table_data()
    app.run()
