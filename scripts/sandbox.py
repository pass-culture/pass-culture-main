""" sandbox script """
#https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
# -*- coding: utf-8 -*-
from pprint import pprint
import traceback
from flask import current_app as app
import json
from os import path
from pathlib import Path
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

    json_path = Path(path.dirname(path.realpath(__file__))) / '..' / 'mock' / 'jsons' / 'users.json'

    with open(json_path) as json_file:
        for user in json.load(json_file):
            if 'hasAllOfferers' in user and user['hasAllOfferers'] == True:
            # un acteur culturel qui peut jouer à rajouter des offres partout
                admin_query = model.User.query.filter_by(email="pctest.admin@btmx.fr")
                if admin_query.count() == 1:
                    admin_user = admin_query.one()
                else:
                    admin_user = model.User()
                    admin_user.publicName = "Utilisateur test admin"
                    admin_user.email = "pctest.admin@btmx.fr"
                    admin_user.departementCode = "93"
                    admin_user.isAdmin = True
                    admin_user.canBook = False
                    admin_user.setPassword("pctestadmin")
                    check_and_save(admin_user)
                    set_from_mock("thumbs", admin_user, 2)
                    for offerer in model.Offerer.query.all():
                        userOfferer = model.UserOfferer()
                        userOfferer.rights = "admin"
                        userOfferer.user = admin_user
                        userOfferer.offerer = offerer
                        check_and_save(userOfferer)
            else:
                # des jeunes qui veulent profiter du pass-culture
                user = model.User(from_dict=user)
                check_and_save(user)
                set_from_mock("thumbs", user, 1)
