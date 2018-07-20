import json
from datetime import datetime, timedelta, timezone
from os import path
from pathlib import Path

import requests as req

from models import Thing
from models.booking import Booking
from models.event import Event
from models.event_occurence import EventOccurence
from models.offer import Offer
from models.offerer import Offerer
from models.user import User
from models.venue import Venue

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
                raise ValueError("Utilisateur inconnu: " + email)
    return r


def create_booking_for_booking_email_test(app, user, offer):
    booking = Booking()
    booking.user = user
    offer.bookings = [booking]
    return booking


def create_user_for_booking_email_test(app):
    user = User()
    user.publicName = 'Test'
    user.email = 'test@email.com'
    return user


def create_event_offer_for_booking_email_test(app):
    offer = Offer()
    offer.bookingLimitDatetime = datetime.utcnow() + timedelta(minutes=2)
    offer.eventOccurence = EventOccurence()
    offer.eventOccurence.beginningDatetime = datetime(2019, 7, 20, 12, 0, 0, tzinfo=timezone.utc)
    offer.eventOccurence.event = Event()
    offer.eventOccurence.event.name = 'Mains, sorts et papiers'
    offer.eventOccurence.venue = _create_venue_for_booking_email_test(app)
    offer.thing = None
    offer.isActive = True

    return offer


def create_thing_offer_for_booking_email_test(app):
    offer = Offer()
    offer.eventOccurence = None
    offer.thing = Thing()
    offer.thing.type = 'Book'
    offer.thing.name = 'Test Book'
    offer.thing.mediaUrls = 'test/urls'
    offer.thing.idAtProviders = '12345'
    offer.isActive = True
    offer.venue = _create_venue_for_booking_email_test(app)
    return offer


def create_offerer_for_booking_email_test(app):
    offerer = Offerer()
    offerer.isActive = 't'
    offerer.address = '123 rue test'
    offerer.postalCode = '93000'
    offerer.city = 'Test city'
    offerer.name = 'Test offerer'
    return offerer


def _create_venue_for_booking_email_test(app):
    venue = Venue()
    venue.address = '123 rue test'
    venue.postalCode = '93000'
    venue.city = 'Test city'
    venue.name = 'Test offerer'
    venue.departementCode = '93'
    return venue
