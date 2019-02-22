""" models event occurrence test """
from datetime import datetime, timedelta

import pytest

from models import PcObject, ApiErrors
from tests.conftest import clean_database
from utils.human_ids import humanize
from utils.includes import EVENT_OCCURRENCE_INCLUDES, OFFER_INCLUDES
from tests.test_utils import create_event_occurrence, \
                             create_event_offer, \
                             create_thing_offer, \
                             create_offerer, \
                             create_stock_from_event_occurrence, \
                             create_venue


@pytest.mark.standalone
@clean_database
def test_beginning_datetime_cannot_be_after_end_datetime(app):
    # given
    offer = create_thing_offer(create_venue(create_offerer()))
    now = datetime.utcnow()
    beginning = now - timedelta(days=5)
    end = beginning - timedelta(days=1)
    occurrence = create_event_occurrence(offer, beginning, end)

    # when
    with pytest.raises(ApiErrors) as e:
        PcObject.check_and_save(occurrence)

    # then
    assert e.value.errors['endDatetime'] == [
        'La date de fin de l\'événement doit être postérieure à la date de début'
    ]


@pytest.mark.standalone
@clean_database
def test_soft_deleted_stocks_do_not_appear_in_asdict(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_event_offer(venue)
    event_occurrence = create_event_occurrence(offer)
    stock1 = create_stock_from_event_occurrence(event_occurrence)
    stock2 = create_stock_from_event_occurrence(event_occurrence)
    stock3 = create_stock_from_event_occurrence(event_occurrence)
    stock4 = create_stock_from_event_occurrence(event_occurrence)
    stock4.isSoftDeleted = True
    PcObject.check_and_save(stock1, stock2, stock3, stock4)

    # When
    event_occurrence_dict = event_occurrence._asdict(include=EVENT_OCCURRENCE_INCLUDES)

    # Then
    retrieved_stock_ids = set([s['id'] for s in event_occurrence_dict['stocks']])
    expected_stock_ids = set([humanize(s_id) for s_id in [stock1.id, stock2.id, stock3.id]])
    assert retrieved_stock_ids == expected_stock_ids

@pytest.mark.standalone
@clean_database
def test_soft_deleted_event_occurences_do_not_appear_in_asdict(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_event_offer(venue)
    eo1 = create_event_occurrence(offer)
    eo2 = create_event_occurrence(offer)
    eo3 = create_event_occurrence(offer)
    eo4 = create_event_occurrence(offer)

    eo4.isSoftDeleted = True
    PcObject.check_and_save(eo1, eo2, eo3, eo4)

    # When
    offer_dict = offer._asdict(include=OFFER_INCLUDES)

    # Then
    retrieved_eo_ids = set([eo['id'] for eo in offer_dict['eventOccurrences']])
    expected_eo_ids = set([humanize(eo_id) for eo_id in [eo1.id, eo2.id, eo3.id]])
    assert retrieved_eo_ids == expected_eo_ids
