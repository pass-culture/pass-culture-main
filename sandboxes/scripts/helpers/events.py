from models import Event
from models.pc_object import PcObject
from utils.human_ids import dehumanize
from utils.logger import logger

def create_or_find_event(event_mock):
    event = Event.query.filter_by(name=event_mock['name']).first()

    logger.info("look event " + event_mock['name'])

    if event is None:
        event = Event(from_dict=event_mock)
        if 'id' in event_mock:
            event.id = dehumanize(event_mock['id'])
        PcObject.check_and_save(event)
        logger.info("created event " + str(event))

    logger.info('--already here-- event' + str(event))

    return event

def create_or_find_events(*event_mocks):
    events_count = str(len(event_mocks))
    logger.info("event mocks " + events_count)

    events = []
    for (event_index, event_mock) in enumerate(event_mocks):
        logger.info(str(event_index) + "/" + events_count)
        event = create_or_find_event(event_mock)
        events.append(event)

    return events
