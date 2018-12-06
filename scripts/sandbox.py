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
                    default="true")
def sandbox(name, clean):
    try:
        with_clean = True if clean == "true" else False
        save_sandbox(name, with_clean)
    except Exception as e:
        print('ERROR: ' + str(e))
        traceback.print_tb(e.__traceback__)
        pprint(vars(e))
