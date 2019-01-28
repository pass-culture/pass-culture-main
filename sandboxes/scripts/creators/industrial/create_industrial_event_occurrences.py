from datetime import datetime, timedelta

from models.pc_object import PcObject
from utils.date import strftime, today
from utils.logger import logger
from utils.test_utils import create_event_occurrence

EVENT_OCCURRENCE_BEGINNING_DATETIMES = [
    today,
    today + timedelta(days=2),
    today + timedelta(days=15)
]

EVENT_OCCURRENCE_MODULO = 2

def create_industrial_event_occurrences(event_offers_by_name):
    logger.info('create_industrial_event_occurrences')

    event_occurrences_by_name = {}

    event_offers = list(event_offers_by_name.values())
    event_offers_with_occurrences = event_offers[::EVENT_OCCURRENCE_MODULO]
    for event_offer_with_occurrences in event_offers_with_occurrences:
        for beginning_datetime in EVENT_OCCURRENCE_BEGINNING_DATETIMES:
            name = "{} / {} / {} ".format(
                event_offer_with_occurrences.eventOrThing.name,
                event_offer_with_occurrences.venue.name,
                strftime(beginning_datetime)
            )
            print('EVENT OCCURRENCE', name)
            event_occurrences_by_name[name] = create_event_occurrence(
                beginning_datetime=strftime(beginning_datetime),
                end_datetime=strftime(beginning_datetime + timedelta(hours=1)),
                offer=event_offer_with_occurrences
            )

    PcObject.check_and_save(*event_occurrences_by_name.values())

    logger.info('created {} event_occurrences'.format(len(event_occurrences_by_name)))

    return event_occurrences_by_name
