from models.pc_object import PcObject
from utils.logger import logger
from utils.test_utils import create_event

def create_typed_events():

    events_by_name = {}

    events_by_name["Rencontre avec Franck Lepage"] = create_event(
        duration_minutes=60,
        event_name="Rencontre avec Franck Lepage",
        type="EventType.CONFERENCE_DEBAT_DEDICACE",
    )

    events_by_name["Concert de Gael Faye"] = create_event(
        duration_minutes=120,
        event_name="Concert de Gael Faye",
        type="EventType.MUSIQUE",
    )


    events_by_name["PNL chante Marx"] = create_event(
        duration_minutes=10,
        event_name="PNL chante Marx",
        type="EventType.MUSIQUE",
    )

    return events_by_name
