""" generators """
from datetime import timedelta
import numpy
import requests

from domain.types import get_format_types, get_types_by_value
from models import EventOccurrence,\
                   Event,\
                   Mediation,\
                   Offer,\
                   Offerer,\
                   Stock,\
                   Thing,\
                   Venue
from models.auto_increment import get_last_stored_id_of_model
from sandboxes.scripts.utils.params import EVENT_OR_THING_MOCK_NAMES, \
                                           EVENT_OCCURRENCE_BEGINNING_DATETIMES, \
                                           PLACES
from utils.date import strftime
from utils.human_ids import humanize

def get_all_typed_event_offer_mocks(all_typed_event_mocks, all_venue_mocks, starting_id=None):

    pass

def get_all_typed_thing_offer_mocks(all_typed_thing_mocks, all_venue_mocks, starting_id=None):

    

def get_all_typed_event_occurrence_mocks(all_typed_event_offer_mocks, starting_id=None):

    if starting_id is None:
        starting_id = get_last_stored_id_of_model(EventOccurrence)

    incremented_id = starting_id

    event_occurrence_mocks = []
    for event_offer_mock in all_typed_event_offer_mocks:
        for beginning_datetime in EVENT_OCCURRENCE_BEGINNING_DATETIMES:
            event_occurrence_mock = {
                "beginningDatetime": strftime(beginning_datetime),
                "endDatetime": strftime(beginning_datetime + timedelta(hours=1)),
                "id": humanize(incremented_id),
                "offerId": event_offer_mock['id']
            }

            incremented_id += 1

            event_occurrence_mocks.append(event_occurrence_mock)

    return event_occurrence_mocks

def get_all_typed_event_stock_mocks(all_typed_event_occurrence_mocks, starting_id=None):

    if starting_id is None:
        starting_id = get_last_stored_id_of_model(EventOccurrence)

    incremented_id = starting_id

    stock_mocks = []
    for event_occurrence_mock in all_typed_event_occurrence_mocks:

        stock_mock = {
            "available": 10,
            "eventOccurrenceId": event_occurrence_mock['id'],
            "id": humanize(incremented_id),
            "price": 10
        }

        incremented_id += 1

        stock_mocks.append(stock_mock)

    return stock_mocks

def get_all_typed_thing_stock_mocks(all_typed_thing_offer_mocks, starting_id=None):

    if starting_id is None:
        starting_id = get_last_stored_id_of_model(Stock)

    incremented_id = starting_id

    stock_mocks = []
    for thing_offer_mock in all_typed_thing_offer_mocks:
        stock_mock = {
            "available": 10,
            "id": humanize(incremented_id),
            "offerId": thing_offer_mock['id'],
            "price": 10
        }

        incremented_id += 1

        stock_mocks.append(stock_mock)

    return stock_mocks

def get_all_typed_event_mediation_mocks(all_typed_event_offer_mocks, starting_id=None):

    if starting_id is None:
        starting_id = get_last_stored_id_of_model(Mediation)

    incremented_id = starting_id

    mediation_mocks = []
    for event_offer_mock in all_typed_event_offer_mocks:
        mediation_mock = {
            "id": humanize(incremented_id),
            "offerId": event_offer_mock['id'],
            "thumbName": event_offer_mock['type']
        }

        incremented_id += 1

        mediation_mocks.append(mediation_mock)

    return mediation_mocks

def get_all_typed_thing_mediation_mocks(all_typed_thing_offer_mocks, starting_id=None):

    if starting_id is None:
        starting_id = get_last_stored_id_of_model(Mediation)

    incremented_id = starting_id

    mediation_mocks = []
    for thing_offer_mock in all_typed_thing_offer_mocks:
        mediation_mock = {
            "id": humanize(incremented_id),
            "offerId": thing_offer_mock['id'],
            "thumbName": thing_offer_mock['type']
        }

        incremented_id += 1

        mediation_mocks.append(mediation_mock)

    return mediation_mocks
