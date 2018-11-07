""" events """
from sandboxes.scripts.utils.generators import get_all_typed_event_mocks
from utils.human_ids import dehumanize, humanize

EVENT_MOCKS = []

SCRATCH_EVENT_MOCKS = [
    {
        "durationMinutes": 60,
        "id": humanize(1),
        "name": "Rencontre avec Franck Lepage",
        "type": "EventType.CONFERENCE_DEBAT_DEDICACE",
        "thumbCount": 1,
        "firstThumbDominantColor": b'\x00\x00\x00'
    },
    {
        "durationMinutes": 120,
        "id": humanize(2),
        "name": "Concert de Gael Faye",
        "type": "EventType.MUSIQUE",
        "thumbCount": 1,
        "firstThumbDominantColor": b'\x00\x00\x00'
    },
    {
        "durationMinutes": 10,
        "id": humanize(3),
        "name": "PNL chante Marx",
        "type": "EventType.MUSIQUE",
        "thumbCount": 1,
        "firstThumbDominantColor": b'\x00\x00\x00'
    }
]
EVENT_MOCKS += SCRATCH_EVENT_MOCKS


ALL_TYPED_EVENT_MOCKS = get_all_typed_event_mocks(
    starting_id=dehumanize(EVENT_MOCKS[-1]['id']) + 1
)
EVENT_MOCKS += ALL_TYPED_EVENT_MOCKS
