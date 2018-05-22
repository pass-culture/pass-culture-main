""" sandbox script """
#https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
from pprint import pprint
import traceback
from flask import current_app as app

from utils.mock import set_from_mock

@app.manager.command
def sandbox():
    try:
        do_sandbox()
    except Exception as e:
        print('ERROR: '+str(e))
        traceback.print_tb(e.__traceback__)
        pprint(vars(e))


def do_sandbox():
    check_and_save = app.model.PcObject.check_and_save
    model = app.model

    # un acteur culturel qui peut jouer a rajouter des offres partout
    pro_user = model.User().query\
                    .filter_by(email="erwan.ledoux@beta.gouv.fr")\
                    .one()
    for offerer in model.Offerer.query.all():
        userOfferer = model.UserOfferer()
        userOfferer.rights = "admin"
        userOfferer.user = pro_user
        userOfferer.offerer = offerer
        check_and_save(userOfferer)
