""" sandbox script """
#https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
# -*- coding: utf-8 -*-
import json
from os import path
from pathlib import Path
from pprint import pprint
import traceback
from flask import current_app as app

from sandboxes import save


@app.manager.command
def init_db_load_testing():
    try:
        populate_json()
        populate_db()
    except Exception as e:
        print('ERROR: '+str(e))
        traceback.print_tb(e.__traceback__)
        pprint(vars(e))


def populate_json():
    json_path = Path(path.dirname(path.realpath(__file__))) / '..' / 'sandboxes' / 'jsons' / 'lt_users.json'

    data = []
    print("Create json file with 150 users")
    for i in range(150):
        user = {}
        user['publicName'] = "User " + str(i) + " for Load Testing"
        user['email'] = "test-lt-"+str(i)+"@load-testing.fr"
        user['departementCode'] = "93"
        user['password'] = "test-lt-"+str(i)
        data.append(user)

    print("Save data to json file")
    with open(json_path, 'w') as outfile:
        json.dump(data, outfile)


def populate_db():
    check_and_save = app.model.PcObject.save
    model = app.model

    json_path = Path(path.dirname(path.realpath(__file__))) / '..' / 'sandboxes' / 'jsons' / 'lt_users.json'

    with open(json_path) as json_file:
        for user_dict in json.load(json_file):
            query = model.User.query.filter_by(email=user_dict['email'])
            print("QUERY COUNT", query.count())
            if query.count() == 0:
                user = model.User(from_dict=user_dict)
                check_and_save(user)
                if 'isAdmin' in user_dict and user_dict['isAdmin']:
                    # un acteur culturel qui peut jouer à rajouter des offres partout
                    # TODO: a terme, le flag isAdmin lui donne tous les droits sans
                    # besoin de faire cette boucle
                    for offerer in model.Offerer.query.all():
                        userOfferer = model.UserOfferer()
                        userOfferer.rights = "admin"
                        userOfferer.user = user
                        userOfferer.offerer = offerer
                        check_and_save(userOfferer)
                    save("thumbs", user, 2)
                else:
                    save("thumbs", user, 1)
