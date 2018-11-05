from datetime import timedelta

from models import EventOccurrence
from models.pc_object import PcObject
from utils.logger import logger

def create_or_find_event_occurrence(event_occurrence_mock, offer=None, store=None):
    if store is None:
        store = {}

    if offer is None:
        offer = store['offers_by_key'][event_occurrence_mock['offerKey']]

    event_occurrence = EventOccurrence.query.filter_by(
        beginningDatetime=event_occurrence_mock['beginningDatetime'],
        offerId=offer.id
    ).first()

    if event_occurrence is None:
        event_occurrence = EventOccurrence(from_dict=event_occurrence_mock)
        event_occurrence.offer = offer
        if event_occurrence.endDatetime is None:
            event_occurrence.endDatetime = event_occurrence.beginningDatetime + timedelta(hours=1)
        PcObject.check_and_save(event_occurrence)
        logger.info("created event_occurrence " + str(event_occurrence))
    else:
        logger.info('--already here-- event occurrence ' + str(event_occurrence))

    return event_occurrence

def create_or_find_event_occurrences(*event_occurrence_mocks, store=None):
    if store is None:
        store = {}

    event_occurrences_count = str(len(event_occurrence_mocks))
    logger.info("event_occurrence mocks " + event_occurrences_count)

    store['event_occurrences_by_key'] = {}

    for (event_occurrence_index, event_occurrence_mock) in enumerate(event_occurrence_mocks):
        logger.info("look event_occurrence " + store['offers_by_key'][event_occurrence_mock['offerKey']].event.name + " " + " " + str(event_occurrence_index) + "/" + event_occurrences_count)
        event_occurrence = create_or_find_event_occurrence(event_occurrence_mock, store=store)
        store['event_occurrences_by_key'][event_occurrence_mock['key']] = event_occurrence
