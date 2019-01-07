from datetime import datetime, timedelta

import pytest

from models.activity import load_activity
from models import PcObject
from repository.stock_queries import find_stocks_of_finished_events_when_no_recap_sent
from tests.conftest import clean_database
from utils.test_utils import create_stock_from_event_occurrence, create_event_occurrence, create_event_offer, \
    create_venue, create_offerer, create_thing_offer, create_stock_from_offer


@pytest.mark.standalone
@clean_database
def test_find_stocks_of_finished_events_when_no_recap_sent(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_event_offer(venue)
    thing_offer = create_thing_offer(venue)
    event_occurrence_past = create_event_occurrence(offer, beginning_datetime=datetime.utcnow() - timedelta(hours=48),
                                                    end_datetime=datetime.utcnow() - timedelta(hours=46))
    event_occurrence_past_2 = create_event_occurrence(offer, beginning_datetime=datetime.utcnow() - timedelta(hours=10),
                                                      end_datetime=datetime.utcnow() - timedelta(hours=2))
    event_occurrence_future = create_event_occurrence(offer, beginning_datetime=datetime.utcnow() + timedelta(hours=46),
                                                      end_datetime=datetime.utcnow() + timedelta(hours=48))
    stock_past = create_stock_from_event_occurrence(event_occurrence_past)
    stock_soft_deleted = create_stock_from_event_occurrence(event_occurrence_past, soft_deleted=True)
    stock_future = create_stock_from_event_occurrence(event_occurrence_future)
    stock_thing = create_stock_from_offer(thing_offer)
    stock_recap_sent = create_stock_from_event_occurrence(event_occurrence_past_2, recap_sent=True)
    PcObject.check_and_save(stock_past, stock_future, stock_thing, stock_soft_deleted, stock_recap_sent)

    # When
    stocks = find_stocks_of_finished_events_when_no_recap_sent().all()

    # Then
    assert stock_past in stocks
    assert stock_future not in stocks
    assert stock_thing not in stocks
    assert stock_soft_deleted not in stocks

@pytest.mark.standalone
@clean_database
def test_create_stock_triggers_insert_activities(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer)
    thing_offer = create_thing_offer(venue)
    stock = create_stock_from_offer(thing_offer)

    # When
    PcObject.check_and_save(stock)

    # Then
    activities = load_activity().query.all()
    assert len(activities) == 5
    assert set(
        ["thing", "offerer", "venue", "thing", "offer", "stock"]
    ) == set(
        [a.table_name for a in activities]
    )
    assert set(
        ["insert"]
    ) == set(
        [a.verb for a in activities]
    )
