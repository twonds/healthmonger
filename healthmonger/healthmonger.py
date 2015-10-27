import flask

# healthmonger modules
import config
import db
import loader
import log

app = flask.Flask(__name__)
app.debug = config.debug
app.config.from_object(config)

db_client = db.Client()


@app.route('/')
def index():
    data = ""
    with app.open_resource(config.APP_PATH+"README.md") as readme:
        data = readme.readlines()
    return "".join(data)


@app.route('/load')
def load_data():
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
    response = "NOT_OK"
    if db_client.data_loaded:
        response = "OK"
    return flask.jsonify({'status': response})


@app.route('/query')
def query():
    args = flask.request.args
    limit = args.get('limit', config.DEFAULT_QUERY_LIMIT)
    offset = args.get('offset', 0)
    q = args.get('q', '')
    table = args.get('table')
    total, result = db_client.search(table, q, limit, offset)
    log.debug(result)
    return flask.jsonify(result)


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
    # Note: This could delay the start of the service.
    loader.download(exists=False)
    load_table_data()
    app.run()
