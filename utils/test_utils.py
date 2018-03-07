import requests as req

API_URL = "http://localhost:5000"

req_with_auth = req.Session()
req_with_auth.auth = ('erwan.ledoux@beta.gouv.fr', 'erwan')
