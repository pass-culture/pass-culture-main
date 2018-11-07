from models import Event
from models.pc_object import PcObject
from utils.human_ids import dehumanize
from utils.logger import logger

def create_or_find_event(event_mock):
    logger.info("look event " + event_mock['name'] + " " + event_mock.get('id'))

    if 'id' in event_mock:
        event = Event.query.get(dehumanize(event_mock['id']))
    else:
        event = Event.query.filter_by(name=event_mock['name']).first()

    if event is None:
        event = Event(from_dict=event_mock)
        if 'id' in event_mock:
            event.id = dehumanize(event_mock['id'])
        PcObject.check_and_save(event)
        logger.info("created event " + str(event))

    logger.info('--already here-- event' + str(event))

    return event
