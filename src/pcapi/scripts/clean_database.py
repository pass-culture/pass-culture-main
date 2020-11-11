# -*- coding: utf-8 -*-
from pprint import pprint
import traceback

from flask import current_app as app

from pcapi.repository.clean_database import clean_all_database


@app.manager.command
def clean():
    try:
        clean_all_database()
    except Exception as e:
        print("ERROR: " + str(e))
        traceback.print_tb(e.__traceback__)
        pprint(vars(e))
