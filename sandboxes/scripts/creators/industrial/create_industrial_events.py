from domain.types import get_formatted_event_or_thing_types
from models.offer_type import EventType
from models.pc_object import PcObject
from sandboxes.scripts.utils.event_mocks import MOCK_ACTIVATION_DESCRIPTION, \
                                                MOCK_ACTIVATION_NAME, \
                                                MOCK_DESCRIPTIONS, \
                                                MOCK_NAMES
from utils.logger import logger
from tests.test_utils import create_event


EVENT_COUNTS_PER_TYPE = 7

def create_industrial_events():
    logger.info('create_industrial_events')

    events_by_name = {}

    event_type_dicts = [
        t for t in get_formatted_event_or_thing_types(with_activation_type=True)
        if t['type'] == 'Event'
    ]

    for type_index in range(0, EVENT_COUNTS_PER_TYPE):

        for (event_type_dict_index, event_type_dict) in enumerate(event_type_dicts):

            mock_index = (type_index + event_type_dict_index) % len(MOCK_NAMES)

            if event_type_dict['value'] == str(EventType.ACTIVATION):
                event_name = MOCK_ACTIVATION_NAME
                description = MOCK_ACTIVATION_DESCRIPTION
            else:
                event_name = MOCK_NAMES[mock_index]
                description = MOCK_DESCRIPTIONS[mock_index]

            name = "{} / {}".format(event_type_dict['value'], MOCK_NAMES[mock_index])
            events_by_name[name] = create_event(
                description=description,
                event_name=event_name,
                event_type=event_type_dict['value'],
                duration_minutes=60
            )

        type_index += len(event_type_dicts)

    PcObject.check_and_save(*events_by_name.values())

    logger.info('created {} events'.format(len(events_by_name)))

    return events_by_name
