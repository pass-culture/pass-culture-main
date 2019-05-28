""" testcafe script """
# -*- coding: utf-8 -*-
from pprint import pprint
import traceback
from flask import current_app as app

from models.pc_object import PcObject
from models.provider import Provider

@app.manager.command
def testcafe():
    try:
        do_testcafe()
    except Exception as e:
        print('ERROR: ' + str(e))
        traceback.print_tb(e.__traceback__)
        pprint(vars(e))

def do_testcafe():
    provider = Provider.query.filter_by(localClass='OpenAgendaEvents').first()
    provider.isActive = True
    PcObject.save(provider)
