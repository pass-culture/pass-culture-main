from datetime import timedelta

from models import EventOccurrence, Offer
from models.pc_object import PcObject
from utils.human_ids import dehumanize
from utils.logger import logger

def create_or_find_event_occurrence(event_occurrence_mock, offer=None):
    if offer is None:
        offer = Offer.query.get(dehumanize(event_occurrence_mock['offerId']))

    logger.info("look event_occurrence")

    event_occurrence = EventOccurrence.query.filter_by(
        beginningDatetime=event_occurrence_mock['beginningDatetime'],
        offerId=offer.id
    ).first()

    if event_occurrence is None:
        event_occurrence = EventOccurrence(from_dict=event_occurrence_mock)
        event_occurrence.offer = offer
        if event_occurrence.endDatetime is None:
            event_occurrence.endDatetime = event_occurrence.beginningDatetime + timedelta(hours=1)
        if 'id' in event_occurrence_mock:
            event_occurrence.id = dehumanize(event_occurrence_mock['id'])
        PcObject.check_and_save(event_occurrence)
        logger.info("created event_occurrence " + str(event_occurrence))
    else:
        logger.info('--already here-- event occurrence ' + str(event_occurrence))

    return event_occurrence

def create_or_find_event_occurrences(*event_occurrence_mocks):
    event_occurrences_count = str(len(event_occurrence_mocks))
    logger.info("event_occurrence mocks " + str(event_occurrences_count))

    event_occurrences = []
    for (event_occurrence_index, event_occurrence_mock) in enumerate(event_occurrence_mocks):
        logger.info(str(event_occurrence_index) + "/" + event_occurrences_count)
        event_occurrence = create_or_find_event_occurrence(event_occurrence_mock)
        event_occurrences.append(event_occurrence)

    return event_occurrences
