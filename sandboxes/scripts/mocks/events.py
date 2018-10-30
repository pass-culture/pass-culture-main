""" events """
from sandboxes.scripts.mocks import get_all_typed_event_mocks

EVENT_MOCKS = []

ALL_TYPED_EVENT_MOCKS = get_all_typed_event_mocks()
EVENT_MOCKS += ALL_TYPED_EVENT_MOCKS

SCRATCH_EVENT_MOCKS = [
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
EVENT_MOCKS += SCRATCH_EVENT_MOCKS
