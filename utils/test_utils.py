import requests as req

API_URL = "http://localhost:5000"


def req_with_auth():
    r = req.Session()
    r.auth = ('pctest.admin@btmx.fr', 'pctestadmin')
    return r
