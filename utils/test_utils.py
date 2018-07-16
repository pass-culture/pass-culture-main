import requests as req
import json
from os import path
from pathlib import Path
from datetime import datetime, timedelta, timezone


API_URL = "http://localhost:5000"


def req_with_auth(email=None, password=None):
    r = req.Session()
    if email is None:
        r.auth = ('pctest.admin@btmx.fr', 'pctestadmin')
    elif password is not None:
        r.auth = (email, password)
    else:
        json_path = Path(path.dirname(path.realpath(__file__))) / '..' / 'mock' / 'jsons' / 'users.json'

        with open(json_path) as json_file:
            for user_json in json.load(json_file):
                print('user_json', user_json)
                if email == user_json['email']:
                    r.auth = (user_json['email'], user_json['password'])
                    break
                raise ValueError("Utilisateur inconnu: " +email)
    return r


def create_booking_for_booking_email_test(app, user, offer):
    booking = app.model.Booking()
    booking.user = user
    offer.bookings = [booking]
    return booking


def create_user_for_booking_email_test(app):
    user = app.model.User()
    user.publicName = 'Test'
    user.email = 'test@email.com'
    return user


def create_offer_for_booking_email_test(app):
    offer = app.model.Offer()
    offer.bookingLimitDatetime = datetime.utcnow() + timedelta(minutes=2)
    offer.eventOccurence = app.model.EventOccurence()
    offer.eventOccurence.beginningDatetime = datetime(2019, 7, 20, 12, 0, 0, tzinfo=timezone.utc)
    offer.eventOccurence.event = app.model.Event()
    offer.eventOccurence.event.name = 'Mains, sorts et papiers'
    offer.eventOccurence.venue = app.model.Venue()
    offer.eventOccurence.venue.departementCode = '93'
    offer.thing = None
    offer.isActive = True
    return offer

def create_offerer_for_booking_email_test(app):
    offerer = app.model.Offerer()
    offerer.isActive = 't'
    offerer.address = '123 rue test'
    offerer.postalCode = '93000'
    offerer.city = 'Test city'
    offerer.name = 'Test offerer'
    return offerer
