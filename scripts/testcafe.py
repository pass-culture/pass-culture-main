""" testcafe script """
# -*- coding: utf-8 -*-
from pprint import pprint
import traceback
from flask import current_app as app

from local_providers.openagenda_events import OpenAgendaEvents
from models.pc_object import PcObject

@app.manager.command
def testcafe():
    try:
        do_testcafe()
    except Exception as e:
        print('ERROR: ' + str(e))
        traceback.print_tb(e.__traceback__)
        pprint(vars(e))

def do_testcafe():
    providerObj = OpenAgendaEvents(None, mock=True)
    providerObj.dbObject.isActive = True
    PcObject.check_and_save(providerObj.dbObject)
