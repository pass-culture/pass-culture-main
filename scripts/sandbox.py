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

    ## USERS

    # un jeune client qui veut profiter du pass-culture
    client_user = model.User()
    client_user.publicName = "Arnaud Bétrémieux"
    client_user.account = 100
    client_user.email = "arnaud.betremieux@beta.gouv.fr"
    client_user.setPassword("arnaud123")
    check_and_save(client_user)
    #set_from_mock("thumbs", client_user, 1)
    client_user.save_thumb('https://avatars3.githubusercontent.com/u/185428?s=400&v=4', 0)

    # un acteur culturel qui peut jouer a rajouter des offres partout
    pro_user = model.User()
    pro_user.publicName = "Erwan Ledoux"
    pro_user.email = "erwan.ledoux@beta.gouv.fr"
    pro_user.setPassword("erwan123")
    check_and_save(pro_user)
    set_from_mock("thumbs", pro_user, 2)

    # OFFERERS
    for offerer in model.Offerer.query.all():
        userOfferer = model.UserOfferer()
        userOfferer.rights = "admin"
        userOfferer.user = pro_user
        userOfferer.offerer = offerer
        check_and_save(userOfferer)
