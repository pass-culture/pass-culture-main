""" generators """
from uuid import uuid1

from domain.types import get_format_types, get_types_by_value
from sandboxes.scripts.mocks.utils.mock_names import EVENT_OR_THING_MOCK_NAMES, \
                                                     EVENT_OCCURRENCE_BEGINNING_DATETIMES
from sandboxes.scripts.mocks.venues import ninety_three_venue,\
                                           virtual_ninety_three_venue

def get_all_event_mocks_by_type():
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

def get_all_thing_mocks_by_type():
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

def get_all_event_offer_mocks_by_type():
    event_mocks = get_all_event_mocks_by_type()

    types_by_value = get_types_by_value()

    offer_mocks = []
    for event_mock in event_mocks:

        offer_mock = {
            "eventName": event_mock['name'],
            "isActive": True,
        }

        # DETERMINE THE MATCHING VENUE
        event_type = types_by_value[event_mock['type']]
        if event_type['offlineOnly']:
            offer_mock['venueName'] = ninety_three_venue['name']
        elif event_type['onlineOnly']:
            offer_mock['venueName'] = virtual_ninety_three_venue['name']
        else:
            offer_mock['venueName'] = ninety_three_venue['name']

        offer_mocks.append(offer_mock)

    return offer_mocks

def get_all_thing_offer_mocks_by_type():
    thing_mocks = get_all_thing_mocks_by_type()

    types_by_value = get_types_by_value()

    offer_mocks = []
    for thing_mock in thing_mocks:
        offer_mock = {
            "key": uuid.uuid1(),
            "isActive": True,
            "thingName": thing_mock['name']
        }

        # DETERMINE THE MATCHING VENUE
        thing_type = types_by_value[thing_mock['type']]
        if thing_type['offlineOnly']:
            offer_mock['venueName'] = ninety_three_venue['name']
        elif thing_type['onlineOnly']:
            offer_mock['venueName'] = virtual_ninety_three_venue['name']
        else:
            offer_mock['venueName'] = ninety_three_venue['name']

        offer_mocks.append(thing_mock)

    return offer_mocks

def get_all_offer_mocks_by_type():
    event_offer_mocks = get_all_event_offer_mocks_by_type()
    thing_offer_mocks = get_all_thing_mocks_by_type()
    return event_offer_mocks + thing_offer_mocks

def get_all_event_occurrence_mocks_by_type():
    event_offer_mocks = get_all_event_offer_mocks_by_type()

    for event_offer_mock in event_offer_mocks:
        for beginning_datetime in EVENT_OCCURRENCE_BEGINNING_DATETIMES:
            event_occurrence_mock = {
                "beginningDatetime": beginning_datetime,
                "offerKey": event_offer_mock['key']
            }
