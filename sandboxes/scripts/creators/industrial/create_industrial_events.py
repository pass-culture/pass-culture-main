from domain.types import get_formatted_event_or_thing_types
from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_event

MOCK_NAMES = [
    "Anaconda",
    "Borneo",
    "D--",
    "Funky",
    "Sun",
    "Topaz"
]

def create_industrial_events():
    logger.info('create_industrial_events')

    events_by_name = {}

    event_types = [t for t in get_formatted_event_or_thing_types() if t['type'] == 'Event']

    mock_count = -1
    for event_type in event_types:

        # WE JUST PARSE THE MOCK NAMES
        # WITH A COUNTER AND RESET THE COUNTER
        # TO ZERO WHEN WE REACH ITS LAST ITEM
        mock_count += 1
        if mock_count > len(MOCK_NAMES) - 1:
            mock_count = 0

        name = event_type['value'] + " / " + MOCK_NAMES[mock_count]
        events_by_name[name] = create_event(
            event_name=name,
            event_type=event_type['value'],
            duration_minutes=60
        )

    PcObject.check_and_save(*events_by_name.values())

    return events_by_name
