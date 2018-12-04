""" sandbox script """
# -*- coding: utf-8 -*-
from pprint import pprint
import traceback
from flask import current_app as app

from sandboxes.scripts.save_sandbox import save_sandbox


@app.manager.option('-n',
                    '--name',
                    help='Sandbox name',
                    default="classic")
@app.manager.option('-c',
                    '--clean',
                    help='Clean database first',
                    default=True)
def sandbox(name, clean):
    try:
        save_sandbox(name, clean)
    except Exception as e:
        print('ERROR: ' + str(e))
        traceback.print_tb(e.__traceback__)
        pprint(vars(e))
