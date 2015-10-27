import requests

class Api:
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
                  'table':table}
        url = self.url+'query'
        r = requests.get(url, params)
        print r.status_code
        print r.json()
        return result

def create():
    return Api()
