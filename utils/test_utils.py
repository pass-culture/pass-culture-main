import json
from datetime import datetime, timedelta, timezone
from os import path
from pathlib import Path

import requests as req

from models import Thing
from models.booking import Booking
from models.event import Event
from models.event_occurence import EventOccurence
from models.occasion import Occasion
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


def create_booking_for_booking_email_test(user, offer):
    booking = Booking()
    booking.user = user
    booking.token = '56789'
    offer.bookings = [booking]
    return booking


def create_user_for_booking_email_test():
    user = User()
    user.publicName = 'Test'
    user.email = 'test@email.com'
    return user


def create_offer_with_event_occasion(price=10):
    offer = Offer()
    offer.price = price
    offer.bookingLimitDatetime = datetime.utcnow() + timedelta(minutes=2)
    offer.eventOccurence = EventOccurence()
    offer.eventOccurence.beginningDatetime = datetime(2019, 7, 20, 12, 0, 0, tzinfo=timezone.utc)
    offer.eventOccurence.occasion = Occasion()
    offer.eventOccurence.occasion.event = Event()
    offer.eventOccurence.occasion.event.name = 'Mains, sorts et papiers'
    offer.eventOccurence.occasion.venue = _create_venue_for_booking_email_test()
    offer.isActive = True

    return offer


def create_offer_with_thing_occasion(price=10):
    offer = Offer()
    offer.price = price
    offer.occasion = Occasion()
    offer.occasion.thing = Thing()
    offer.occasion.thing.type = 'Book'
    offer.occasion.thing.name = 'Test Book'
    offer.occasion.thing.mediaUrls = 'test/urls'
    offer.occasion.thing.idAtProviders = '12345'
    offer.occasion.venue = _create_venue_for_booking_email_test()
    offer.isActive = True
    return offer


def create_offerer():
    offerer = Offerer()
    offerer.isActive = True
    offerer.address = '123 rue test'
    offerer.postalCode = '93000'
    offerer.city = 'Test city'
    offerer.name = 'Test offerer'
    return offerer


def _create_venue_for_booking_email_test():
    venue = Venue()
    venue.bookingEmail = 'reservations@test.fr'
    venue.address = '123 rue test'
    venue.postalCode = '93000'
    venue.city = 'Test city'
    venue.name = 'Test offerer'
    venue.departementCode = '93'
    venue.managingOfferer = create_offerer()
    return venue
