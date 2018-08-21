""" sandbox """
#https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import json
from pprint import pprint
from os import path
from pathlib import Path

from models.pc_object import PcObject
from models import Booking,\
                   Deposit,\
                   EventOccurrence,\
                   Event,\
                   Offer,\
                   Offerer,\
                   Stock,\
                   User,\
                   UserOfferer,\
                   Venue
from utils.mock import set_from_mock


def do_sandbox():
    json_path = Path(path.dirname(path.realpath(__file__))) / '..' / 'mock' / 'jsons' / 'users.json'

    with open(json_path) as json_file:
        for (user_index, user_dict) in enumerate(json.load(json_file)):
            query = User.query.filter_by(email=user_dict['email'])
            if query.count() == 0:
                user = User(from_dict=user_dict)
                user.validationToken = None
                PcObject.check_and_save(user)
                pprint(vars(user))
                print("CREATED user")
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
                set_from_mock("thumbs", user, user_index)


    json_path = Path(path.dirname(path.realpath(__file__))) / '..' / 'mock' / 'jsons' / 'offerers.json'
    offerers = []
    with open(json_path) as json_file:
        for obj in json.load(json_file):
            query = Offerer.query.filter_by(name=obj['name'])
            if query.count() == 0:
                offerer = Offerer(from_dict=obj)
                PcObject.check_and_save(offerer)
                print("CREATED offerer")
                pprint(vars(offerer))
                offerers.append(offerer)
            else:
                offerers.append(query.one())

    json_path = Path(path.dirname(path.realpath(__file__))) / '..' / 'mock' / 'jsons' / 'venues.json'
    venues = []
    with open(json_path) as json_file:
        for obj in json.load(json_file):
            query = Venue.query.filter_by(name=obj['name'])
            if query.count() == 0:
                venue = Venue(from_dict=obj)
                venue.managingOfferer = offerers[obj['offererIndex']]
                PcObject.check_and_save(venue)
                print("CREATED venue")
                pprint(vars(venue))
                venues.append(venue)
            else:
                venues.append(query.one())

    json_path = Path(path.dirname(path.realpath(__file__))) / '..' / 'mock' / 'jsons' / 'events.json'
    events = []
    with open(json_path) as json_file:
        for obj in json.load(json_file):
            query = Event.query.filter_by(name=obj['name'])
            if query.count() == 0:
                event = Event(from_dict=obj)
                PcObject.check_and_save(event)
                print("CREATED event")
                pprint(vars(event))
                events.append(event)
            else:
                events.append(query.one())

    json_path = Path(path.dirname(path.realpath(__file__))) / '..' / 'mock' / 'jsons' / 'offers.json'
    offers = []
    with open(json_path) as json_file:
        for obj in json.load(json_file):
            if 'eventIndex' in obj:
                event_or_thing = events[obj['eventIndex']]
                is_event = True
                query = Offer.query.filter_by(eventId=event_or_thing.id)
            else:
                event_or_thing = events[obj['thingIndex']]
                is_event = False
                query = Offer.query.filter_by(thingId=event_or_thing.id)
            if query.count() == 0:
                offer = Offer(from_dict=obj)
                if is_event:
                    offer.event = event_or_thing
                else:
                    offer.thing = event_or_thing
                PcObject.check_and_save(offer)
                print("CREATED offer")
                pprint(vars(offer))
                offers.append(offer)
            else:
                offers.append(query.one())

    json_path = Path(path.dirname(path.realpath(__file__))) / '..' / 'mock' / 'jsons' / 'event_occurrences.json'
    event_occurrences = []
    with open(json_path) as json_file:
        for obj in json.load(json_file):
            offer = offers[obj['offerIndex']]
            query = EventOccurrence.query.filter_by(offerId=offer.id)
            if query.count() == 0:
                event_occurrence = EventOccurrence(from_dict=obj)
                event_occurrence.offer = offer
                event_occurrence.beginningDatetime = datetime.now() + timedelta(days=1)
                event_occurrence.endDatetime = event_occurrence.beginningDatetime + timedelta(hours=1)
                PcObject.check_and_save(event_occurrence)
                print("CREATED event_occurrence")
                pprint(vars(event_occurrence))
                event_occurrences.append(event_occurrence)
            else:
                event_occurrences.append(query.one())

    json_path = Path(path.dirname(path.realpath(__file__))) / '..' / 'mock' / 'jsons' / 'stocks.json'
    stocks = []
    with open(json_path) as json_file:
        for obj in json.load(json_file):
            event_occurrence = event_occurrences[obj['eventOccurrenceIndex']]
            query = Stock.query.filter_by(eventOccurrenceId=event_occurrence.id)
            if query.count() == 0:
                stock = Stock(from_dict=obj)
                stock.eventOccurrence = event_occurrence
                stock.offer = offers[obj['offerIndex']]
                PcObject.check_and_save(stock)
                print("CREATED stock")
                pprint(vars(stock))
                stocks.append(stock)
            else:
                stocks.append(query.one())

    json_path = Path(path.dirname(path.realpath(__file__))) / '..' / 'mock' / 'jsons' / 'deposits.json'
    deposits = []
    with open(json_path) as json_file:
        for obj in json.load(json_file):
            user = User.query.filter_by(email=obj['userEmail']).one()
            query = Deposit.query.filter_by(userId=user.id)
            if query.count() == 0:
                deposit = Deposit(from_dict=obj)
                deposit.user = user
                PcObject.check_and_save(deposit)
                print("CREATED deposit")
                pprint(vars(deposit))
                deposits.append(deposit)

    json_path = Path(path.dirname(path.realpath(__file__))) / '..' / 'mock' / 'jsons' / 'bookings.json'
    bookings = []
    with open(json_path) as json_file:
        for obj in json.load(json_file):
            stock = stocks[obj['stockIndex']]
            user = User.query.filter_by(email=obj['userEmail']).one()
            query = Booking.query.filter_by(stockId=stock.id)
            if query.count() == 0:
                booking = Booking(from_dict=obj)
                booking.stock = stock
                booking.user = user
                booking.amount = stock.price
                PcObject.check_and_save(booking)
                print("CREATED booking")
                pprint(vars(booking))
                bookings.append(booking)
