from datetime import datetime
from datetime import time
from datetime import timedelta
import logging

from pcapi.core.offers.models import Offer
from pcapi.models.event_occurence import EventOccurrence
from pcapi.sandboxes.scripts.utils.select import remove_every
import pcapi.utils.date as date_utils


logger = logging.getLogger(__name__)


TODAY = datetime.combine(datetime.utcnow(), time(hour=20))
EVENT_OCCURRENCE_BEGINNING_DATETIMES = [
    TODAY,
    TODAY + timedelta(days=2),
    TODAY + timedelta(days=15),
]

EVENT_OFFERS_WITH_OCCURRENCES_REMOVE_MODULO = 3


def create_industrial_event_occurrences(event_offers_by_name: dict[str, Offer]) -> dict[str, EventOccurrence]:
    logger.info("create_industrial_event_occurrences")

    event_occurrences_by_name = {}

    event_offers = list(event_offers_by_name.values())

    event_offers_with_occurrences = remove_every(event_offers, EVENT_OFFERS_WITH_OCCURRENCES_REMOVE_MODULO)

    for event_offer_with_occurrences in event_offers_with_occurrences:
        for beginning_datetime in EVENT_OCCURRENCE_BEGINNING_DATETIMES:
            name = "{} / {} / {} ".format(
                event_offer_with_occurrences.product.name,
                event_offer_with_occurrences.venue.name,
                beginning_datetime.strftime(date_utils.DATE_ISO_FORMAT),
            )
            event_occurrences_by_name[name] = EventOccurrence(
                beginning_datetime=beginning_datetime,
                offer=event_offer_with_occurrences,
            )

    return event_occurrences_by_name
