""" geoip script """
# -*- coding: utf-8 -*-
from pprint import pprint
import traceback
from flask import current_app as app

from utils.geoip import geoip
from utils.mock import set_from_mock

@app.manager.command
def geoip():
    try:
        do_geoip()
    except Exception as e:
        print('ERROR: '+str(e))
        traceback.print_tb(e.__traceback__)
        pprint(vars(e))


def do_geoip():
    download_fresh_db()
