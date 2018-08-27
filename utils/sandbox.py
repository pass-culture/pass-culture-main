""" sandbox """
#https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import json
from pprint import pprint

from mock.scripts import booking_mocks,\
                         deposit_mocks,\
                         event_mocks,\
                         event_occurrence_mocks,\
                         offer_mocks,\
                         offerer_mocks,\
                         stock_mocks,\
                         user_mocks,\
                         venue_mocks
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

    for (user_index, user_mock) in enumerate(user_mocks):
        query = User.query.filter_by(email=user_mock['email'])
        if query.count() == 0:
            user = User(from_dict=user_mock)
            user.validationToken = None
            PcObject.check_and_save(user)
            pprint(vars(user))
            print("CREATED user")
            if 'isAdmin' in user_mock and user_mock['isAdmin']:
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


    offerers = []
    for offerer_mock in offerer_mocks:
        query = Offerer.query.filter_by(name=offerer_mock['name'])
        if query.count() == 0:
            offerer = Offerer(from_dict=offerer_mock)
            PcObject.check_and_save(offerer)
            print("CREATED offerer")
            pprint(vars(offerer))
            offerers.append(offerer)
        else:
            offerers.append(query.one())

    venues = []
    for venue_mock in venue_mocks:
        query = Venue.query.filter_by(name=venue_mock['name'])
        if query.count() == 0:
            venue = Venue(from_dict=venue_mock)
            venue.managingOfferer = offerers[venue_mock['offererIndex']]
            PcObject.check_and_save(venue)
            print("CREATED venue")
            pprint(vars(venue))
            venues.append(venue)
        else:
            venues.append(query.one())

    events = []
    for event_mock in event_mocks:
        query = Event.query.filter_by(name=event_mock['name'])
        if query.count() == 0:
            event = Event(from_dict=event_mock)
            PcObject.check_and_save(event)
            print("CREATED event")
            pprint(vars(event))
            events.append(event)
        else:
            events.append(query.one())

    offers = []
    for offer_mock in offer_mocks:
        if 'eventIndex' in offer_mock:
            event_or_thing = events[offer_mock['eventIndex']]
            is_event = True
            query = Offer.query.filter_by(eventId=event_or_thing.id)
        else:
            event_or_thing = events[offer_mock['thingIndex']]
            is_event = False
            query = Offer.query.filter_by(thingId=event_or_thing.id)

        venue = venues[offer_mock['venueIndex']]
        query.filter_by(venueId=venue.id)

        if query.count() == 0:
            offer = Offer(from_dict=offer_mock)
            if is_event:
                offer.event = event_or_thing
            else:
                offer.thing = event_or_thing
            offer.venue = venue
            PcObject.check_and_save(offer)
            print("CREATED offer")
            pprint(vars(offer))
            offers.append(offer)
        else:
            offers.append(query.one())

    event_occurrences = []
    for event_occurrence_mock in event_occurrence_mocks:
        offer = offers[event_occurrence_mock['offerIndex']]
        query = EventOccurrence.query.filter_by(offerId=offer.id)
        if query.count() == 0:
            event_occurrence = EventOccurrence(from_dict=event_occurrence_mock)
            event_occurrence.offer = offer
            event_occurrence.beginningDatetime = datetime.now() + timedelta(days=1)
            event_occurrence.endDatetime = event_occurrence.beginningDatetime + timedelta(hours=1)
            PcObject.check_and_save(event_occurrence)
            print("CREATED event_occurrence")
            pprint(vars(event_occurrence))
            event_occurrences.append(event_occurrence)
        else:
            event_occurrences.append(query.one())

    stocks = []
    for stock_mock in stock_mocks:
        event_occurrence = event_occurrences[stock_mock['eventOccurrenceIndex']]
        query = Stock.query.filter_by(eventOccurrenceId=event_occurrence.id)
        if query.count() == 0:
            stock = Stock(from_dict=stock_mock)
            stock.eventOccurrence = event_occurrence
            PcObject.check_and_save(stock)
            print("CREATED stock")
            pprint(vars(stock))
            stocks.append(stock)
        else:
            stocks.append(query.one())

    deposits = []
    for deposit_mock in deposit_mocks:
        user = User.query.filter_by(email=deposit_mock['userEmail']).one()
        query = Deposit.query.filter_by(userId=user.id)
        if query.count() == 0:
            deposit = Deposit(from_dict=deposit_mock)
            deposit.user = user
            PcObject.check_and_save(deposit)
            print("CREATED deposit")
            pprint(vars(deposit))
            deposits.append(deposit)

    bookings = []
    for booking_mock in booking_mocks:
        stock = stocks[booking_mock['stockIndex']]
        user = User.query.filter_by(email=booking_mock['userEmail']).one()
        query = Booking.query.filter_by(stockId=stock.id)
        if query.count() == 0:
            booking = Booking(from_dict=booking_mock)
            booking.stock = stock
            booking.user = user
            booking.amount = stock.price
            PcObject.check_and_save(booking)
            print("CREATED booking")
            pprint(vars(booking))
            bookings.append(booking)
