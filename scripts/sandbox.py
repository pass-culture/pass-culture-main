""" sandbox script """
# -*- coding: utf-8 -*-
from pprint import pprint
import traceback
from flask import current_app as app

from utils.sandbox import do_sandbox

@app.manager.option('-n',
                    '--name',
                    help='Sandbox name')
def sandbox(name):
    try:
        do_sandbox(name)
    except Exception as e:
        print('ERROR: ' + str(e))
        traceback.print_tb(e.__traceback__)
        pprint(vars(e))