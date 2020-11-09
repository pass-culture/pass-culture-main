# -*- coding: utf-8 -*-
from pprint import pprint
import traceback

from flask import current_app as app

from pcapi.sandboxes.scripts.save_sandbox import save_sandbox
from pcapi.sandboxes.scripts.testcafe_helpers import print_all_testcafe_helpers
from pcapi.sandboxes.scripts.testcafe_helpers import print_testcafe_helper
from pcapi.sandboxes.scripts.testcafe_helpers import print_testcafe_helpers


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
        with_clean = clean == "true"
        save_sandbox(name, with_clean)
    except Exception as e:
        print('ERROR: ' + str(e))
        traceback.print_tb(e.__traceback__)
        pprint(vars(e))

@app.manager.option('-n',
                    '--name',
                    help='Sandboxes getters module name',
                    default=None)
@app.manager.option('-g',
                    '--getter',
                    help='Sandboxes getters function name',
                    default=None)
def sandbox_to_testcafe(name, getter):
    try:
        if name is None:
            print_all_testcafe_helpers()
        elif getter is None:
            print_testcafe_helpers(name)
        else:
            print_testcafe_helper(name, getter)
    except Exception as e:
        print('ERROR: ' + str(e))
        traceback.print_tb(e.__traceback__)
        pprint(vars(e))
