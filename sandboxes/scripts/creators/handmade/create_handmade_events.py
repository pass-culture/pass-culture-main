from models.pc_object import PcObject
from models.offer_type import EventType
from utils.logger import logger
from tests.test_utils import create_event

def create_handmade_events():
    logger.info("create_handmade_events")

    events_by_name = {}

    name = "Rencontre avec Franck Lepage"
    events_by_name[name] = create_event(
        duration_minutes=60,
        event_name=name,
        event_type=str(EventType.CONFERENCE_DEBAT_DEDICACE)
    )

    name = "Concert de Gael Faye"
    events_by_name[name] = create_event(
        duration_minutes=120,
        event_name=name,
        event_type=str(EventType.MUSIQUE)
    )

    name = "PNL chante Marx"
    events_by_name[name] = create_event(
        duration_minutes=10,
        event_name=name,
        event_type=str(EventType.MUSIQUE)
    )

    name = "Le temps des cerises en mode mixolydien"
    events_by_name[name] = create_event(
        duration_minutes=55,
        event_name=name,
        event_type=str(EventType.MUSIQUE)
    )

    PcObject.check_and_save(*events_by_name.values())

    logger.info('created {} events'.format(len(events_by_name)))

    return events_by_name
