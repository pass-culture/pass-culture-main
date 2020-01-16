# -*- coding: utf-8 -*-
import traceback
from pprint import pprint

from flask import current_app as app

from repository.clean_database import clean_all_database


@app.manager.command
def clean():
    try:
        clean_all_database()
    except Exception as e:
        print('ERROR: ' + str(e))
        traceback.print_tb(e.__traceback__)
        pprint(vars(e))
