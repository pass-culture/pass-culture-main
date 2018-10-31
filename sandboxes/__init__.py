
""" sandbox """
#https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior
# -*- coding: utf-8 -*-
from datetime import datetime, timedelta
import json
from pprint import pprint
import sys

from models.pc_object import PcObject
from models import Booking,\
                   Deposit,\
                   EventOccurrence,\
                   Event,\
                   Mediation,\
                   Offer,\
                   Offerer,\
                   Stock,\
                   Thing,\
                   User,\
                   UserOfferer,\
                   Venue
from sandboxes.scripts.mocks import *
from sandboxes.scripts import sandbox_light, sandbox_webapp
from sandboxes.utils import store_public_object_from_sandbox_assets

def save_sandbox_in_db(name):
    function_name = "sandboxes.scripts.sandbox_" + name
    sandbox_module = sys.modules[function_name]

    offerers_count = str(len(sandbox_module.OFFERER_MOCKS))
    print("OFFERER MOCKS " + offerers_count)
    offerers_by_key = {}
    for (offerer_index, offerer_mock) in enumerate(sandbox_module.OFFERER_MOCKS):
        print("LOOK offerer " + offerer_mock['name'] + " " + str(offerer_index) + "/" + offerers_count)
        query = Offerer.query.filter_by(name=offerer_mock['name'])
        if query.count() == 0:
            offerer = Offerer(from_dict=offerer_mock)
            PcObject.check_and_save(offerer)
            print("CREATED offerer " + str(offerer) + " " + offerer_mock['name'])
        else:
            offerer = query.first()
            print('--ALREADY HERE-- offerer' + str(offerer))
        offerers_by_key[offerer_mock['key']] = offerer

    users_count = str(len(sandbox_module.USER_MOCKS))
    print("USER MOCKS " + users_count)
    users_by_email = {}
    for (user_index, user_mock) in enumerate(sandbox_module.USER_MOCKS):
        print("LOOK user " + user_mock['email'] + " " + str(user_index) + "/" + users_count)
        query = User.query.filter_by(email=user_mock['email'])
        if query.count() == 0:
            user = User(from_dict=user_mock)
            user.validationToken = None
            PcObject.check_and_save(user)
            print("CREATED user " + str(user) + " " + user_mock['email'])
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
            store_public_object_from_sandbox_assets("thumbs", user, user_index)
        else:
            user = query.first()
            print('--ALREADY HERE-- user' + str(user))
        users_by_email[user_mock['email']] = user

    user_offerers_count = str(len(sandbox_module.USER_OFFERER_MOCKS))
    print("USER OFFERER MOCKS " + user_offerers_count)
    for (user_offerer_index, user_offerer_mock) in enumerate(sandbox_module.USER_OFFERER_MOCKS):
        print("LOOK user_offerer " + user_offerer_mock['userEmail'] + user_offerer_mock['offererKey'] + " " + str(user_offerer_index) + "/" + user_offerers_count)

        user = users_by_email[user_offerer_mock['userEmail']]
        offerer = offerers_by_key[user_offerer_mock['offererKey']]

        query = UserOfferer.query.filter_by(
            userId=user.id,
            offererId=offerer.id
        )
        if query.count() == 0:
            user_offerer = UserOfferer(from_dict=user_offerer_mock)
            user_offerer.user = user
            user_offerer.offerer = offerer
            PcObject.check_and_save(user_offerer)
            print("CREATED user_offerer" + str(user_offerer))
        else:
            user_offerer = query.first()
            print('--ALREADY HERE-- user_offerer' + str(user_offerer))

    venues_count = str(len(sandbox_module.VENUE_MOCKS))
    print("VENUE MOCKS " + venues_count)
    venues_by_key = {}
    for (venue_index, venue_mock) in enumerate(sandbox_module.VENUE_MOCKS):
        print("LOOK venue " + venue_mock['offererKey'] + " " + venue_mock['name'] + " " + str(venue_index) + "/" + venues_count)
        offerer = offerers_by_key[venue_mock['offererKey']]
        query = Venue.query.filter_by(
            managingOffererId=offerer.id,
            name=venue_mock['name']
        )
        if query.count() == 0:
            venue = Venue(from_dict=venue_mock)
            venue.managingOfferer = offerers_by_key[venue_mock['offererKey']]
            PcObject.check_and_save(venue)
            print("CREATED venue " + venue_mock['offererKey'] + " " + venue_mock['name'])
        else:
            venue = query.first()
            print('--ALREADY HERE-- venue' + str(venue))
        venues_by_key[venue_mock['key']] = venue

    events_count = str(len(sandbox_module.EVENT_MOCKS))
    print("EVENT MOCKS " + events_count)
    events_by_key = {}
    for (event_index,event_mock) in enumerate(sandbox_module.EVENT_MOCKS):
        print("LOOK event " + event_mock['name'] + " " + str(event_index) + "/" + events_count)
        query = Event.query.filter_by(name=event_mock['name'])
        if query.count() == 0:
            event = Event(from_dict=event_mock)
            PcObject.check_and_save(event)
            print("CREATED event " + str(event) + " " + event_mock['name'])
        else:
            event = query.first()
            print('--ALREADY HERE-- event' + str(event))
        events_by_key[event_mock['key']] = event

    things_count = str(len(sandbox_module.THING_MOCKS))
    print("THING MOCKS " + things_count)
    things_by_key = {}
    for (thing_index, thing_mock) in enumerate(sandbox_module.THING_MOCKS):
        print("LOOK thing " + thing_mock['name'] + " " + str(thing_index) + "/" + things_count)
        query = Thing.query.filter_by(name=thing_mock['name'])
        if query.count() == 0:
            thing = Thing(from_dict=thing_mock)
            PcObject.check_and_save(thing)
            print("CREATED thing " + str(thing) + " " + thing_mock['name'])
        else:
            thing = query.first()
            print('--ALREADY HERE-- thing' + str(thing))
        things_by_key[thing_mock['key']] = thing

    offers_count = str(len(sandbox_module.OFFER_MOCKS))
    print("OFFER MOCKS " + offers_count)
    offers_by_key = {}
    for (offer_index, offer_mock) in enumerate(sandbox_module.OFFER_MOCKS):
        if 'eventKey' in offer_mock:
            print("LOOK offer " + events_by_key[offer_mock['eventKey']].name + " " + venues_by_key[offer_mock['venueKey']].name+ " " + str(offer_index) + "/" + offers_count)
            event_or_thing = events_by_key[offer_mock['eventKey']]
            is_event = True
            query = Offer.query.filter_by(eventId=event_or_thing.id)
        else:
            print("LOOK offer " + things_by_key[offer_mock['thingKey']].name + " " + venues_by_key[offer_mock['venueKey']].name+ " " + str(offer_index) + "/" + offers_count)
            event_or_thing = things_by_key[offer_mock['thingKey']]
            is_event = False
            query = Offer.query.filter_by(thingId=event_or_thing.id)

        venue = venues_by_key[offer_mock['venueKey']]
        query = query.filter_by(venueId=venue.id)

        if query.count() == 0:
            offer = Offer(from_dict=offer_mock)
            if is_event:
                offer.event = event_or_thing
            else:
                offer.thing = event_or_thing
            offer.venue = venue
            PcObject.check_and_save(offer)
            print("CREATED offer " + str(offer))
        else:
            offer = query.first()
            print('--ALREADY HERE-- offer' + str(offer))
        offers_by_key[offer_mock['key']] = offer

    event_occurrences_count = str(len(sandbox_module.EVENT_OCCURRENCE_MOCKS))
    print("EVENT OCCURRENCE MOCKS " + event_occurrences_count)
    event_occurrences_by_key = {}
    for (event_occurrence_index, event_occurrence_mock) in enumerate(sandbox_module.EVENT_OCCURRENCE_MOCKS):
        print("LOOK event occurrence " + event_occurrence_mock['offerKey'] + " " + str(event_occurrence_index) + "/" + event_occurrences_count)
        offer = offers_by_key[event_occurrence_mock['offerKey']]
        query = EventOccurrence.query.filter_by(
            beginningDatetime=event_occurrence_mock['beginningDatetime'],
            offerId=offer.id
        )
        if query.count() == 0:
            event_occurrence = EventOccurrence(from_dict=event_occurrence_mock)
            event_occurrence.offer = offer
            if event_occurrence.endDatetime is None:
                event_occurrence.endDatetime = event_occurrence.beginningDatetime + timedelta(hours=1)
            PcObject.check_and_save(event_occurrence)
            print("CREATED event_occurrence " + str(event_occurrence))
        else:
            event_occurrence = query.first()
            print('--ALREADY HERE-- event occurrence' + str(event_occurrence))
        event_occurrences_by_key[event_occurrence_mock['key']] = event_occurrence

    stocks_count = str(len(sandbox_module.STOCK_MOCKS))
    print("STOCK MOCKS " + stocks_count)
    stocks_by_key = {}
    for (stock_index,stock_mock) in enumerate(sandbox_module.STOCK_MOCKS):
        if 'eventOccurrenceKey' in stock_mock:
            print("LOOK stock " + stock_mock['eventOccurrenceKey'] + " " + str(stock_index) + "/" + stocks_count)
            event_occurrence = event_occurrences_by_key[stock_mock['eventOccurrenceKey']]
            query = Stock.queryNotSoftDeleted().filter_by(eventOccurrenceId=event_occurrence.id)
        else:
            print("LOOK stock " + stock_mock['offerKey'] + " " + str(stock_index) + "/" + stocks_count)
            offer = offers_by_key[stock_mock['offerKey']]
            query = Stock.queryNotSoftDeleted().filter_by(offerId=offer.id)

        if query.count() == 0:
            stock = Stock(from_dict=stock_mock)
            if 'eventOccurrenceKey' in stock_mock:
                stock.eventOccurrence = event_occurrence
            else:
                stock.offer = offer
            PcObject.check_and_save(stock)
            print("CREATED stock " + str(stock))
        else:
            stock = query.first()
            print('--ALREADY HERE-- stock' + str(stock))
        stocks_by_key[stock_mock['key']] = stock

    deposits_count = str(len(sandbox_module.DEPOSIT_MOCKS))
    print("DEPOSIT MOCKS " + deposits_count)
    deposits = []
    for (deposit_index,deposit_mock) in enumerate(sandbox_module.DEPOSIT_MOCKS):
        print("LOOK deposit " + deposit_mock['userEmail'] + " " + str(deposit_index) + "/" + deposits_count)
        user = User.query.filter_by(email=deposit_mock['userEmail']).one()
        query = Deposit.query.filter_by(userId=user.id)
        if query.count() == 0:
            deposit = Deposit(from_dict=deposit_mock)
            deposit.user = user
            PcObject.check_and_save(deposit)
            print("CREATED deposit " + str(deposit))
        else:
            deposit = query.first()
            print('--ALREADY HERE-- deposit' + str(deposit))
        deposits.append(deposit)

    mediations_count = str(len(sandbox_module.MEDIATION_MOCKS))
    print("MEDIATION MOCKS " + mediations_count)
    mediations_by_key = {}
    for (mediation_index, mediation_mock) in enumerate(sandbox_module.MEDIATION_MOCKS):
        print("LOOK mediation " + mediation_mock['offerKey'] + " " + str(mediation_index) + "/" + mediations_count)
        offer = offers_by_key[mediation_mock['offerKey']]
        query = Mediation.query.filter_by(
            offerId=offer.id
        )
        if query.count() == 0:
            mediation = Mediation(from_dict=mediation_mock)
            mediation.offer = offer
            PcObject.check_and_save(mediation)
            print("CREATED mediation " + str(mediation))
        else:
            mediation = query.first()
            print('--ALREADY HERE-- mediation' + str(mediation))

        if 'thumbName' not in mediation_mock:
            if offer.event:
                event = Event.query.filter_by(
                    id=offer.event.id
                ).first()
                thumb_name = event.type
            else:
                thing = Thing.query.filter_by(
                    id=offer.thing.id
                ).first()
                thumb_name = thing.type
        else:
            thumb_name = mediation_mock['thumbName']
        store_public_object_from_sandbox_assets("thumbs", mediation, thumb_name)
        mediations_by_key[mediation_mock['key']] = mediation

    recommendations_count = str(len(sandbox_module.RECOMMENDATION_MOCKS))
    print("RECOMMENDATION MOCKS " + recommendations_count)
    recommendations_by_key = {}
    for (recommendation_index, recommendation_mock) in enumerate(sandbox_module.RECOMMENDATION_MOCKS):
        print("LOOK recommendation " + recommendation_mock['mediationKey'] + " " + str(recommendation_index) + "/" + recommendations_count)
        mediation = mediations_by_key[recommendation_mock['mediationKey']]
        user = User.query.filter_by(email=recommendation_mock['userEmail']).one()
        query = Mediation.query.filter_by(
            mediationId=stock.id,
            userId=user.id,
        )
        if query.count() == 0:
            recommendation = Recommendation(from_dict=recommendation_mock)
            recommendation.mediation = mediation
            recommendation.user = user
            PcObject.check_and_save(recommendation)
            print("CREATED recommendation " + str(recommendation))
        else:
            recommendation = query.first()
            print('--ALREADY HERE-- recommendation' + str(recommendation))
        recommendations_by_key[recommendation_mock['key']] = recommendation

    bookings_count = str(len(sandbox_module.BOOKING_MOCKS))
    print("BOOKING MOCKS " + bookings_count)
    bookings_by_key = {}
    for (booking_index, booking_mock) in enumerate(sandbox_module.BOOKING_MOCKS):
        print("LOOK booking " + booking_mock['stockKey'] + " " + str(booking_index) + "/" + bookings_count)
        stock = stocks_by_key[booking_mock['stockKey']]
        user = User.query.filter_by(email=booking_mock['userEmail']).one()
        query = Booking.query.filter_by(
            stockId=stock.id,
            userId=user.id,
            token=booking_mock['token']
        )
        if query.count() == 0:
            booking = Booking(from_dict=booking_mock)
            booking.stock = stock
            booking.user = user
            booking.amount = stock.price
            PcObject.check_and_save(booking)
            print("CREATED booking " + str(booking))
        else:
            booking = query.first()
            print('--ALREADY HERE-- booking' + str(booking))
        bookings_by_key[booking_mock['key']] = booking
