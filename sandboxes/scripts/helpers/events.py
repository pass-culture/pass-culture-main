from models import Event
from models.pc_object import PcObject
from utils.logger import logger

def create_or_find_event(event_mock):
    query = Event.query.filter_by(name=event_mock['name'])

    if query.count() == 0:
        event = Event(from_dict=event_mock)
        PcObject.check_and_save(event)
        logger.info("created event " + str(event))
    else:
        event = query.first()
        logger.info('--already here-- event' + str(event))

    return event

def create_or_find_events(*event_mocks, store=None):
    if store is None:
        store = {}

    events_count = str(len(event_mocks))
    logger.info("event mocks " + events_count)

    store['events_by_key'] = {}

    for (event_index, event_mock) in enumerate(event_mocks):
        logger.info("look event " + event_mock['name'] + " " + str(event_index) + "/" + events_count)
        event = create_or_find_event(event_mock)
        store['events_by_key'][event_mock['key']] = event
