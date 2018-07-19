""" sandbox script """
#https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
# -*- coding: utf-8 -*-
import json
from pprint import pprint
import traceback
from os import path
from pathlib import Path
from flask import current_app as app

from models.offerer import Offerer
from models.user import User
from models.user_offerer import UserOfferer
from models.pc_object import PcObject
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
    json_path = Path(path.dirname(path.realpath(__file__))) / '..' / 'mock' / 'jsons' / 'users.json'

    with open(json_path) as json_file:
        for user_dict in json.load(json_file):
            query = User.query.filter_by(email=user_dict['email'])
            print("QUERY COUNT", query.count())
            if query.count() == 0:
                user = User(from_dict=user_dict)
                user.validationToken = None
                from pprint import pprint
                pprint(vars(user))
                PcObject.check_and_save(user)
                if 'isAdmin' in user_dict and user_dict['isAdmin']:
                    # un acteur culturel qui peut jouer à rajouter des offres partout
                    # TODO: a terme, le flag isAdmin lui donne tous les droits sans
                    # besoin de faire cette boucle
                    for offerer in Offerer.query.all():
                        userOfferer = UserOfferer()
                        userOfferer.rights = "admin"
                        userOfferer.user = user
                        userOfferer.offerer = offerer
                        PcObject.check_and_save(userOfferer)
                    set_from_mock("thumbs", user, 2)
                else:
                    set_from_mock("thumbs", user, 1)
