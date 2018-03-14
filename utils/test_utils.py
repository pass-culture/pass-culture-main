import requests as req

API_URL = "http://localhost:5000"


def req_with_auth():
    r = req.Session()
    r.auth = ('erwan.ledoux@beta.gouv.fr', 'erwan123')
    return r
