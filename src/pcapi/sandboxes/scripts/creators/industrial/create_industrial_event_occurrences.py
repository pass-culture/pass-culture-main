from datetime import timedelta

from pcapi.model_creators.specific_creators import create_event_occurrence
from pcapi.sandboxes.scripts.utils.select import remove_every
from pcapi.utils.date import TODAY
from pcapi.utils.date import strftime
from pcapi.utils.logger import logger


EVENT_OCCURRENCE_BEGINNING_DATETIMES = [
    TODAY,
    TODAY + timedelta(days=2),
    TODAY + timedelta(days=15)
]

EVENT_OFFERS_WITH_OCCURRENCES_REMOVE_MODULO = 3

def create_industrial_event_occurrences(event_offers_by_name):
    logger.info('create_industrial_event_occurrences')

    event_occurrences_by_name = {}

    event_offers = list(event_offers_by_name.values())

    event_offers_with_occurrences = remove_every(
        event_offers,
        EVENT_OFFERS_WITH_OCCURRENCES_REMOVE_MODULO
    )

    for event_offer_with_occurrences in event_offers_with_occurrences:
        for beginning_datetime in EVENT_OCCURRENCE_BEGINNING_DATETIMES:
            name = "{} / {} / {} ".format(
                event_offer_with_occurrences.product.name,
                event_offer_with_occurrences.venue.name,
                strftime(beginning_datetime)
            )
            event_occurrences_by_name[name] = create_event_occurrence(
                beginning_datetime=strftime(beginning_datetime),
                offer=event_offer_with_occurrences
            )

    return event_occurrences_by_name
