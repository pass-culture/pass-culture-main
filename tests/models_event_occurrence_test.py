from datetime import datetime, timedelta

import pytest

from models import PcObject, ApiErrors
from tests.conftest import clean_database
from utils.human_ids import humanize
from utils.includes import EVENT_OCCURRENCE_INCLUDES
from utils.test_utils import create_event_occurrence, create_thing_offer, create_venue, create_offerer, \
    create_stock_from_event_occurrence, create_event_offer


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
    stock1 = create_stock_from_event_occurrence(offerer, event_occurrence)
    stock2 = create_stock_from_event_occurrence(offerer, event_occurrence)
    stock3 = create_stock_from_event_occurrence(offerer, event_occurrence)
    stock4 = create_stock_from_event_occurrence(offerer, event_occurrence)
    stock4.isSoftDeleted = True
    PcObject.check_and_save(stock1, stock2, stock3, stock4)

    # When
    event_occurrence_dict = event_occurrence._asdict(include=EVENT_OCCURRENCE_INCLUDES)

    # Then
    retrieved_stock_ids = set(map(lambda x: x['id'], event_occurrence_dict['stocks']))
    expected_stock_ids = set(map(humanize, [stock1.id, stock2.id, stock3.id]))
    assert retrieved_stock_ids == expected_stock_ids