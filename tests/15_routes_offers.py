from datetime import datetime, timedelta
from flask import current_app as app, Flask
from flask_script import Manager
from sqlalchemy import desc

from utils.human_ids import humanize
from utils.test_utils import API_URL, req, req_with_auth
from utils.token import random_token


app = Flask(__name__)


def create_app(env=None):
    app.env = env
    return app


app.manager = Manager(create_app)


def test_10_get_offers_should_return_a_list_of_offers():
    r = req_with_auth().get(API_URL + '/offers')
    assert r.status_code == 200
    offers = r.json()
    assert len(offers) > 0


def test_11_modify_offer():
    r_before = req_with_auth().get(API_URL + '/offers/EY')
    assert r_before.status_code == 200
    r_mod = req_with_auth().patch(API_URL + '/offers/EY',
                                json={'price': 1234})
    assert r_mod.status_code == 200
    r_after = req_with_auth().get(API_URL + '/offers/EY')
    assert r_after.status_code == 200
    assert r_after.json()['price'] == 1234

#TODO: check offer modification with missing items or incorrect values


def test_12_create_offer():
    offer_data = {'price': 1222,
                  'offererId': humanize(3),
                  'venueId': humanize(3),
                  'thingId': humanize(1)
                 }
    r_create = req_with_auth().post(API_URL + '/offers/',
                                  json=offer_data)
    assert r_create.status_code == 201
    id = r_create.json()['id']
    r_check = req_with_auth().get(API_URL + '/offers/'+id)
    assert r_check.status_code == 200
    created_offer_data = r_check.json()
    for (key, value) in offer_data.items():
        assert created_offer_data[key] == offer_data[key]
    #TODO: check thumb presence


def test_13_search_offers_by_author():
    r = req_with_auth().get(API_URL + '/offers?search=Jules')
    assert r.status_code == 200
    offers = r.json()
    assert len(offers) > 0


def test_14_update_offer_available_should_check_bookings():
    with app.app_context():
        import models
        offer = app.model.Offer()
        offer.venueId = 1
        offer.offererId = 1
        offer.thingId = 1
        offer.price = 0
        offer.available = 1
        offer.bookingLimitDatetime = datetime.utcnow() + timedelta(minutes=2)
        app.model.PcObject.check_and_save(offer)

        offerId= offer.id

        booking = app.model.Booking()
        booking.offerId = offerId
        booking.recommendationId = 1
        booking.token = random_token()
        booking.userId = 1
        app.model.PcObject.check_and_save(booking)

    r_update = req_with_auth().patch(API_URL + '/offers/'+humanize(offerId),
                                     json={'available': 0})
    assert r_update.status_code == 400
    assert 'available' in r_update.json()
