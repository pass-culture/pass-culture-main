""" sandbox script """
#https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
import json
from pprint import pprint
import traceback
from os import path
from pathlib import Path
from flask import current_app as app

from models.deposit import Deposit
from models.booking import Booking
from models.event_occurrence import EventOccurrence
from models.event import Event
from models.pc_object import PcObject
from models.stock import Stock
from models.offerer import Offerer
from models.user import User
from models.user_offerer import UserOfferer
from models.venue import Venue
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


    json_path = Path(path.dirname(path.realpath(__file__))) / '..' / 'mock' / 'jsons' / 'offerers.json'
    offerers = []
    with open(json_path) as json_file:
        for obj in json.load(json_file):
            query = Offerer.query.filter_by(name=obj['name'])
            if query.count() == 0:
                offerer = Offerer(from_dict=obj)
                offerer.save()
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
                venue.save()
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
                event.save()
                print("CREATED event")
                pprint(vars(event))
                events.append(event)
            else:
                events.append(query.one())

    json_path = Path(path.dirname(path.realpath(__file__))) / '..' / 'mock' / 'jsons' / 'event_occurrences.json'
    event_occurrences = []
    with open(json_path) as json_file:
        for obj in json.load(json_file):
            event = events[obj['eventIndex']]
            query = EventOccurrence.query.filter_by(eventId=event.id)
            if query.count() == 0:
                event_occurrence = EventOccurrence(from_dict=obj)
                event_occurrence.event = event
                event_occurrence.offerer = offerers[obj['offererIndex']]
                event_occurrence.beginningDatetime = datetime.now() + timedelta(days=1)
                event_occurrence.endDatetime = event_occurrence.beginningDatetime + timedelta(hours=1)
                event_occurrence.save()
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
                stock.offerer = offerers[obj['offererIndex']]
                stock.save()
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
                deposit.save()
                print("CREATED deposit")
                pprint(vars(deposit))
                deposits.append(deposit)

    json_path = Path(path.dirname(path.realpath(__file__))) / '..' / 'mock' / 'jsons' / 'bookings.json'
    bookings = []
    with open(json_path) as json_file:
        for obj in json.load(json_file):
            stock = stocks[obj['offerIndex']]
            user = User.query.filter_by(email=obj['userEmail']).one()
            query = Booking.query.filter_by(stockId=stock.id)
            if query.count() == 0:
                booking = Booking(from_dict=obj)
                booking.stock = stock
                booking.user = user
                booking.amount = offer.price
                booking.save()
                print("CREATED booking")
                pprint(vars(booking))
                bookings.append(booking)





