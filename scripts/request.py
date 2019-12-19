""" request """
# -*- coding: utf-8 -*-
from pprint import pprint

from flask import current_app as app

from tests.conftest import TestClient
from tests.model_creators.generic_creators import API_URL


@app.manager.command
def get(url, authenticated=False):
    if authenticated:
        r = TestClient().with_auth().get(API_URL + url)
    else:
        r = TestClient().get(API_URL + url)
    if r.headers.get('content-type') == 'application/json':
        pprint(r.json())
    else:
        print(r.text)
