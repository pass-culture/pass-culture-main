from models.pc_object import PcObject
from models.offer_type import EventType
from utils.logger import logger
from utils.test_utils import create_event

def create_handmade_events():
    logger.info("create_handmade_events")

    events_by_name = {}

    events_by_name["Rencontre avec Franck Lepage"] = create_event(event_name="Rencontre avec Franck Lepage",
                                                                  event_type=str(EventType.CONFERENCE_DEBAT_DEDICACE),
                                                                  duration_minutes=60)

    events_by_name["Concert de Gael Faye"] = create_event(event_name="Concert de Gael Faye",
                                                          event_type=str(EventType.MUSIQUE), duration_minutes=120)


    events_by_name["PNL chante Marx"] = create_event(event_name="PNL chante Marx", event_type=str(EventType.MUSIQUE),
                                                     duration_minutes=10)

    PcObject.check_and_save(*events_by_name.values())

    return events_by_name
