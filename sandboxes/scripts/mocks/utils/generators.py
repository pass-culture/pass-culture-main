""" generators """

from domain.types import get_format_types, get_types_by_value
from sandboxes.scripts.mocks.utils.mock_names import EVENT_OR_THING_MOCK_NAMES
from sandboxes.scripts.mocks.venues import ninety_three_venue, virtual_ninety_three_venue

def get_all_event_mocks_by_type():
    event_types = [t for t in get_format_types() if t['type'] == 'Event']

    event_mocks = []
    mock_count = -1
    for event_type in event_types:

        # WE JUST PARSE THE MOCK NAMES
        # WITH A COUNTER AND RESET THE COUNTER
        # TO ZERO WHEN WE REACH ITS LAST ITEM
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

def get_all_offer_mocks_by_type():
    event_mocks = get_all_event_mocks_by_type()
    thing_mocks = get_all_thing_mocks_by_type()

    types_by_value = get_types_by_value()

    offer_mocks = []
    for event_mock in event_mocks:

        offer_mock = {
            "eventName": event_mock['name'],
            "isActive": True,
        }

        # DETERMINE THE MATCHING VENUE
        if types_by_value[event_mock['type']]['isOfflineOnly']:
            offer_mock['venueName'] = ninety_three_venue['name']
        elif types_by_value[event_mock['type']]['isOnlineOnly']:
            offer_mock['venueName'] = virtual_ninety_three_venue['name']
        else:
            offer_mock['venueName'] = ninety_three_venue['name']

        offer_mocks.append(offer_mock)

    for thing_mock in thing_mocks:
        offer_mock = {
            "isActive": True,
            "thingName": thing_mock['name'],
            "venueName": "LE GRAND REX PARIS"
        }
        offer_mocks.append(thing_mock)

    return offer_mocks
