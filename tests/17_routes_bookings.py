from datetime import datetime, timedelta
from flask import Flask
from flask_script import Manager

from glob import glob
from inspect import isclass
from utils.human_ids import humanize
from utils.test_utils import API_URL, req, req_with_auth


app = Flask(__name__)


def create_app(env=None):
    app.env = env
    return app


app.manager = Manager(create_app)

savedCounts = {}


def test_10_create_booking():
    booking_json = {
        'offerId': humanize(3),
        'recommendationId': humanize(1)
    }
    r_create = req_with_auth().post(API_URL + '/bookings', json=booking_json)
    assert r_create.status_code == 201
    id = r_create.json()['id']
    r_check = req_with_auth().get(API_URL + '/bookings/'+id)
    assert r_check.status_code == 200
    created_booking_json = r_check.json()
    for (key, value) in booking_json.items():
        assert created_booking_json[key] == booking_json[key]


def test_11_create_booking_should_not_work_past_limit_date():
    with app.app_context():
        import models
        expired_offer = app.model.Offer()
        expired_offer.venueId = 1
        expired_offer.offererId = 1
        expired_offer.thingId = 1
        expired_offer.price = 0
        expired_offer.bookingLimitDatetime = datetime.now() - timedelta(seconds=1)
        app.model.PcObject.check_and_save(expired_offer)

        booking_json = {
            'offerId': humanize(expired_offer.id),
            'recommendationId': humanize(1)
        }

    r_create = req_with_auth().post(API_URL + '/bookings', json=booking_json)
    assert r_create.status_code == 400
    assert 'global' in r_create.json()
    assert 'date limite' in r_create.json()['global'][0]


def test_12_create_booking_should_work_before_limit_date():
    with app.app_context():
        import models
        ok_offer = app.model.Offer()
        ok_offer.venueId = 1
        ok_offer.offererId = 1
        ok_offer.thingId = 1
        ok_offer.price = 0
        ok_offer.bookingLimitDatetime = datetime.now() + timedelta(minutes=2)
        app.model.PcObject.check_and_save(ok_offer)

        booking_json = {
            'offerId': humanize(ok_offer.id),
            'recommendationId': humanize(1)
        }

    r_create = req_with_auth().post(API_URL + '/bookings', json=booking_json)
    assert r_create.status_code == 201
    id = r_create.json()['id']
    r_check = req_with_auth().get(API_URL + '/bookings/'+id)
    created_booking_json = r_check.json()
    for (key, value) in booking_json.items():
        assert created_booking_json[key] == booking_json[key]
