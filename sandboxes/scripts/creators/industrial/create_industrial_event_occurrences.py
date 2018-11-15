from datetime import timedelta

from models.pc_object import PcObject
from sandboxes.scripts.utils.params import EVENT_OCCURRENCE_BEGINNING_DATETIMES
from utils.date import strftime, today
from utils.logger import logger
from utils.test_utils import create_event_occurrence

def create_industrial_event_occurrences(event_offers_by_name):
    logger.info('create_industrial_event_occurrences')

    event_occurrences_by_name = {}

    for event_offer in event_offers_by_name.values():
        for beginning_datetime in EVENT_OCCURRENCE_BEGINNING_DATETIMES:
            name = "{} / {} / {} ".format(
                event_offer.eventOrThing.name,
                event_offer.venue.name,
                strftime(beginning_datetime)
            )

            # SPECIAL MORE DELAY FOR EVENT OCCURRENCE IN FAR AWAY TZ
            # BECAUSE OTHERWISE TODAY EVENTS ARE ALREADY FINISHED
            # IN THEIR TZ
            if beginning_datetime == today \
                and event_offer.venue.managingOfferer.departementCode == "97":
                beginning_datetime = beginning_datetime + timedelta(days=1)

            event_occurrences_by_name[name] = create_event_occurrence(
                beginning_datetime=strftime(beginning_datetime),
                end_datetime=strftime(beginning_datetime + timedelta(hours=1)),
                offer=event_offer
            )

    PcObject.check_and_save(*event_occurrences_by_name.values())

    return event_occurrences_by_name
