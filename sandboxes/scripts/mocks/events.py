""" events """

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
    
event_mocks = [
    {
        "durationMinutes": 60,
        "name": "Rencontre avec Franck Lepage",
        "type": "EventType.CONFERENCE_DEBAT_DEDICACE",
        "thumbCount": 1,
        "firstThumbDominantColor": b'\x00\x00\x00'
    },
    {
        "durationMinutes": 120,
        "name": "Concert de Gael Faye",
        "type": "EventType.MUSIQUE",
        "thumbCount": 1,
        "firstThumbDominantColor": b'\x00\x00\x00'
    },
    {
        "durationMinutes": 10,
        "name": "PNL chante Marx",
        "type": "EventType.MUSIQUE",
        "thumbCount": 1,
        "firstThumbDominantColor": b'\x00\x00\x00'
    }
]
