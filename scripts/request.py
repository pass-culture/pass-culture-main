""" request """
# -*- coding: utf-8 -*-
from pprint import pprint
from flask import current_app as app

from tests.test_utils import API_URL, req, req_with_auth

@app.manager.command
def get(url, authenticated=False):
    if authenticated:
        r = req_with_auth.get(API_URL+url)
    else:
        r = req.get(API_URL+url)
    if r.headers.get('content-type') == 'application/json':
        pprint(r.json())
    else:
        print(r.text)
