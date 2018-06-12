import requests as req
import json
from os import path
from pathlib import Path


API_URL = "http://localhost:5000"


def req_with_auth(email=None):
    r = req.Session()
    if email is None:
        r.auth = ('pctest.admin@btmx.fr', 'pctestadmin')
    else:
        json_path = Path(path.dirname(path.realpath(__file__))) / '..' / 'mock' / 'jsons' / 'users.json'

        with open(json_path) as json_file:
            for user_json in json.load(json_file):
                print('user_json', user_json)
                if email == user_json['email']:
                    r.auth = (user_json['email'], user_json['password'])
                    break
                raise ValueError("Utilisateur inconnu: " +email)
    return r
