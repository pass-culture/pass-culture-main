""" generators """
from uuid import uuid1

from domain.types import get_format_types, get_types_by_value
from sandboxes.scripts.mocks.utils.mock_names import EVENT_OR_THING_MOCK_NAMES, \
                                                     EVENT_OCCURRENCE_BEGINNING_DATETIMES
from sandboxes.scripts.mocks.venues import NINETY_THREE_VENUE_MOCK,\
                                           VIRTUAL_NINETY_THREE_VENUE_MOCK

def get_all_typed_event_mocks():
    event_types = [t for t in get_format_types() if t['type'] == 'Event']

    event_mocks = []
    mock_count = -1
    for event_type in event_types:

        # WE JUST PARSE THE MOCK NAMES
        # WITH A COUNTER AND RESET THE COUNTER
        # TO ZERO WHEN WE REACH ITS LAST ITEM
        mock_count += 1
        if mock_count > len(EVENT_OR_THING_MOCK_NAMES) - 1:
            mock_count = 0

        event_mock = {
            "durationMinutes": 60,
            "firstThumbDominantColor": b'\x00\x00\x00',
            "name": EVENT_OR_THING_MOCK_NAMES[mock_count],
            "type": event_type['value'],
            "thumbCount": 1
        }
        event_mocks.append(event_mock)

    return event_mocks

def get_all_typed_thing_mocks():
    thing_types = [t for t in get_format_types() if t['type'] == 'Thing']

    thing_mocks = []
    mock_count = -1
    for thing_type in thing_types:

        # WE JUST PARSE THE MOCK NAMES
        # WITH A COUNTER AND RESET THE COUNTER
        # TO ZERO WHEN WE REACH ITS LAST ITEM
        mock_count += 1
        if mock_count > len(EVENT_OR_THING_MOCK_NAMES) - 1:
            mock_count = 0

        thing_mock = {
            "firstThumbDominantColor": b'\x00\x00\x00',
            "name": EVENT_OR_THING_MOCK_NAMES[mock_count],
            "type": thing_type['value'],
            "thumbCount": 1
        }
        thing_mocks.append(thing_mock)

    return thing_mocks

def get_all_typed_event_offer_mocks(all_typed_event_mocks):

    types_by_value = get_types_by_value()

    offer_mocks = []
    for event_mock in all_typed_event_mocks:

        offer_mock = {
            "key": str(uuid1()),
            "eventName": event_mock['name'],
            "isActive": True,
        }

        # DETERMINE THE MATCHING VENUE
        event_type = types_by_value[event_mock['type']]
        if event_type['offlineOnly']:
            offer_mock['venueKey'] = NINETY_THREE_VENUE_MOCK['key']
        elif event_type['onlineOnly']:
            offer_mock['venueKey'] = VIRTUAL_NINETY_THREE_VENUE_MOCK['key']
        else:
            offer_mock['venueKey'] = NINETY_THREE_VENUE_MOCK['key']

        offer_mocks.append(offer_mock)

    return offer_mocks

def get_all_typed_thing_offer_mocks(all_typed_thing_mocks):

    types_by_value = get_types_by_value()

    offer_mocks = []
    for thing_mock in all_typed_thing_mocks:
        offer_mock = {
            "key": str(uuid1()),
            "isActive": True,
            "thingName": thing_mock['name']
        }

        # DETERMINE THE MATCHING VENUE
        thing_type = types_by_value[thing_mock['type']]
        if thing_type['offlineOnly']:
            offer_mock['venueKey'] = NINETY_THREE_VENUE_MOCK['key']
        elif thing_type['onlineOnly']:
            offer_mock['venueKey'] = VIRTUAL_NINETY_THREE_VENUE_MOCK['key']
        else:
            offer_mock['venueKey'] = NINETY_THREE_VENUE_MOCK['key']

        offer_mocks.append(offer_mock)

    return offer_mocks

def get_all_typed_event_occurrence_mocks(all_typed_event_offer_mocks):

    event_occurrence_mocks = []
    for event_offer_mock in all_typed_event_offer_mocks:
        for beginning_datetime in EVENT_OCCURRENCE_BEGINNING_DATETIMES:
            event_occurrence_mock = {
                "beginningDatetime": beginning_datetime,
                "key": str(uuid1()),
                "offerKey": event_offer_mock['key']
            }

            event_occurrence_mocks.append(event_occurrence_mock)

    return event_occurrence_mocks

def get_all_typed_event_stock_mocks(all_typed_event_occurrence_mocks):

    stock_mocks = []
    for event_occurrence_mock in all_typed_event_occurrence_mocks:
        stock_mock = {
            "available": 10,
            "eventOccurrenceKey": event_occurrence_mock['key'],
            "key": str(uuid1()),
            "price": 10
        }

        stock_mocks.append(stock_mock)

    return stock_mocks

def get_all_typed_thing_stock_mocks(all_typed_thing_offer_mocks):

    stock_mocks = []
    for thing_offer_mock in all_typed_thing_offer_mocks:
        stock_mock = {
            "available": 10,
            "offerKey": thing_offer_mock['key'],
            "key": str(uuid1()),
            "price": 10
        }

        stock_mocks.append(stock_mock)

    return stock_mocks
