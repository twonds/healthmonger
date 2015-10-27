import requests

class Api:
    """Simple class library for making requests to the API.
    This should be replaced by the official api module to ensure testing of both and
    not have divergent code.
    """
    url = 'http://localhost:5000/'

    def load_data(self):
        # XXX - this can be authenticated or limited by network
        return requests.get(self.url+'load')

    def status(self):
        status = "NOT_OK"
        r = requests.get(self.url+'status')
        if r.status_code == 200:
            status = r.json().get('status', "NOT_OK")
        self.server_status = status
        return self.server_status

    def query(self, table, attribute, values):
        result = None
        query = "("
        if attribute:
            query = query + attribute
        query = query + ")"
        params = {'q': query,
                  'table':table,
                  'filter': values}
        url = self.url+'query'
        r = requests.get(url, params)
        return r.json()

def create():
    return Api()
