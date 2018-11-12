from domain.types import get_format_types
from models.pc_object import PcObject
from sandboxes.scripts.utils.params import EVENT_OR_THING_MOCK_NAMES
from utils.logger import logger
from utils.test_utils import create_event

def create_grid_events():
    logger.info('create_grid_events')

    events_by_name = {}

    event_types = [t for t in get_format_types() if t['type'] == 'Event']

    mock_count = -1
    for event_type in event_types:

        # WE JUST PARSE THE MOCK NAMES
        # WITH A COUNTER AND RESET THE COUNTER
        # TO ZERO WHEN WE REACH ITS LAST ITEM
        mock_count += 1
        if mock_count > len(EVENT_OR_THING_MOCK_NAMES) - 1:
            mock_count = 0

        name = event_type['value'] + " " + EVENT_OR_THING_MOCK_NAMES[mock_count]
        events_by_name[name] = create_event(
            event_name=name,
            duration_minutes=60,
            type=event_type['value'],
        )

    PcObject.check_and_save(*events_by_name.values())

    return events_by_name
