# -*- coding: utf-8 -*-
from flask import current_app as app
from utils.test_utils import API_URL, req, req_with_auth
from pprint import pprint


@app.manager.command
def get(url, authenticated=False):
    print(authenticated)
    if authenticated:
        r = req_with_auth.get(API_URL+url)
    else:
        r = req.get(API_URL+url)
    if r.headers.get('content-type') == 'application/json':
        pprint(r.json())
    else:
        print(r.text)
