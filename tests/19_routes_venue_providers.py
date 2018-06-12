from flask import Flask
from flask_script import Manager

from utils.human_ids import humanize
from utils.test_utils import API_URL, req_with_auth


app = Flask(__name__)


def create_app(env=None):
    app.env = env
    return app


app.manager = Manager(create_app)

#with app.app_context():
#    import models
#    import local_providers
#    openagenda_provider = app.model.Provider.getByClassName('OpenAgendaEvents')
#
#
#def test_10_create_venue_provider():
#    vp_data = {'providerId': humanize(openagenda_provider.id),
#               'venueIdAtOfferProvider': '49050769'}
#    r_create = req_with_auth().post(API_URL + '/venue_providers/AE',
#                                    json=vp_data)
#    assert r_create.status_code == 201
#    assert 'id' in r_create.json()
#    #TODO: wait and check for events from openagenda
#
#
#def test_11_delete_venue_provider():
#    r_delete = req_with_auth().post(API_URL + '/venue_providers/AE/'
#                                            +humanize(openagenda_provider.id)
#                                            +'/'
#                                            +'49050769')
#    assert r_delete.status_code == 200
