from models.pc_object import PcObject
from models.offer_types import EventType
from utils.logger import logger
from utils.test_utils import create_event

def create_scratch_events():
    logger.info("create_scratch_events")

    events_by_name = {}

    events_by_name["Rencontre avec Franck Lepage"] = create_event(
        duration_minutes=60,
        event_name="Rencontre avec Franck Lepage",
        event_type=str(EventType.CONFERENCE_DEBAT_DEDICACE)
    )

    events_by_name["Concert de Gael Faye"] = create_event(
        duration_minutes=120,
        event_name="Concert de Gael Faye",
        event_type=str(EventType.MUSIQUE)
    )


    events_by_name["PNL chante Marx"] = create_event(
        duration_minutes=10,
        event_name="PNL chante Marx",
        event_type=str(EventType.MUSIQUE)
    )

    PcObject.check_and_save(*events_by_name.values())

    return events_by_name
