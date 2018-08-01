import json
import random
import string
from datetime import datetime, timedelta, timezone
from os import path
from pathlib import Path

import requests as req

from models import Thing, Deposit
from models.booking import Booking
from models.event import Event
from models.event_occurrence import EventOccurrence
from models.offer import Offer
from models.stock import Stock
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


def create_booking_for_booking_email_test(user, stock, is_cancellation=False):
    booking = Booking()
    booking.stock = stock
    booking.user = user
    booking.token = '56789'
    if not is_cancellation:
        stock.bookings = [booking]
    return booking


def create_user_for_booking_email_test():
    user = User()
    user.publicName = 'Test'
    user.email = 'test@email.com'
    return user


def create_stock_with_event_offer(price=10, beginning_datetime_future=True):
    stock = Stock()
    stock.price = price
    stock.eventOccurrence = EventOccurrence()
    if beginning_datetime_future:
        stock.eventOccurrence.beginningDatetime = datetime(2019, 7, 20, 12, 0, 0, tzinfo=timezone.utc)
        stock.bookingLimitDatetime = datetime.utcnow() + timedelta(minutes=2)
    else:
        stock.eventOccurrence.beginningDatetime = datetime(2017, 7, 20, 12, 0, 0, tzinfo=timezone.utc)
        stock.bookingLimitDatetime = datetime.utcnow() - timedelta(days=800)
    stock.eventOccurrence.offer = Offer()
    stock.eventOccurrence.offer.event = Event()
    stock.eventOccurrence.offer.event.name = 'Mains, sorts et papiers'
    stock.eventOccurrence.offer.venue = _create_venue_for_booking_email_test()
    stock.isActive = True


def create_stock_with_thing_offer(price=10):
    stock = Stock()
    stock.price = price
    stock.offer = create_thing_offer()
    stock.offer.venue = _create_venue_for_booking_email_test()
    stock.isActive = True
    return stock

def create_stock_with_thing_offer(price=10):
    stock = Stock()
    stock.price = price
    stock.offer = create_thing_offer()
    stock.offer.venue = _create_venue_for_booking_email_test()
    stock.isActive = True
    return stock


def create_thing_offer():
    offer = Offer()
    offer.thing = Thing()
    offer.thing.type = 'Book'
    offer.thing.name = 'Test Book'
    offer.thing.mediaUrls = 'test/urls'
    offer.thing.idAtProviders = ''.join(random.choices(string.digits, k=13))
    offer.thing.extraData = {'author': 'Test Author'}
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


def create_deposit(user, amount=50):
    deposit = Deposit()
    deposit.user = user
    deposit.source = "Test money"
    deposit.amount = amount
    return deposit
