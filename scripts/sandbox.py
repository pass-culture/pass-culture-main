""" sandbox script """
# -*- coding: utf-8 -*-
from pprint import pprint
import traceback
from flask import current_app as app

from sandboxes import do


@app.manager.option('-n',
                    '--name',
                    help='Sandbox name',
                    default="classic")
def sandbox(name):
    try:
        do(name)
    except Exception as e:
        print('ERROR: ' + str(e))
        traceback.print_tb(e.__traceback__)
        pprint(vars(e))
