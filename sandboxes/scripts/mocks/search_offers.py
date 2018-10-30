""" search offers """

from domain.types import get_format_types

mock_names = [
    "Anaconda",
    "Borneo",
    "D--",
    "Funky",
    "Sun",
    "Topaz"
]

def get_all_events_by_type():
    event_types = [t for t in get_format_types() if t['type'] == 'Event']

    events = []
    mock_count = -1
    for event_type in event_types:

        # WE JUST PARSE THE MOCK NAMES
        # WITH A COUNTER AND RESET THE COUNTER
        # TO ZERO WHEN WE REACH ITS LAST ITEM
        if mock_count > len(mock_names) - 1:
            mock_count = 0

        event = {
            "durationMinutes": 60,
            "firstThumbDominantColor": b'\x00\x00\x00',
            "name": mock_names[mock_count],
            "type": event_type['value'],
            "thumbCount": 1
        }
        events.append(event)

    return events

def get_all_things_by_type():
    thing_types = [t for t in get_format_types() if t['type'] == 'Thing']

    things = []
    mock_count = -1
    for thing_type in thing_types:

        # WE JUST PARSE THE MOCK NAMES
        # WITH A COUNTER AND RESET THE COUNTER
        # TO ZERO WHEN WE REACH ITS LAST ITEM
        if mock_count > len(mock_names) - 1:
            mock_count = 0

        thing = {
            "firstThumbDominantColor": b'\x00\x00\x00',
            "name": mock_names[mock_count],
            "type": thing_type['value'],
            "thumbCount": 1
        }
        things.append(thing)

    return things
