from datetime import datetime, timedelta

from models import Offer, Thing, Event
from utils.test_utils import create_event_occurrence

now = datetime.utcnow()
two_days_ago = now - timedelta(days=2)
four_days_ago = now - timedelta(days=4)
five_days_from_now = now + timedelta(days=5)
ten_days_from_now = now + timedelta(days=10)


def test_date_range_is_none_if_offer_is_on_a_thing():
    # given
    offer = Offer()
    offer.thing = Thing()
    offer.eventOccurrences = []

    # then
    assert offer.dateRange is None


def test_date_range_matches_the_occurrence_if_only_one_occurrence():
    # given
    offer = Offer()
    offer.event = Event()
    offer.eventOccurrences = [
        create_event_occurrence(offer, beginning_datetime=two_days_ago, end_datetime=five_days_from_now)
    ]

    # then
    assert offer.dateRange == [two_days_ago, five_days_from_now]


def test_date_range_starts_at_first_beginning_date_time_and_ends_at_last_end_date_time():
    # given
    offer = Offer()
    offer.event = Event()
    offer.eventOccurrences = [
        create_event_occurrence(offer, beginning_datetime=two_days_ago, end_datetime=five_days_from_now),
        create_event_occurrence(offer, beginning_datetime=four_days_ago, end_datetime=five_days_from_now),
        create_event_occurrence(offer, beginning_datetime=four_days_ago, end_datetime=ten_days_from_now),
        create_event_occurrence(offer, beginning_datetime=two_days_ago, end_datetime=ten_days_from_now)
    ]

    # then
    assert offer.dateRange == [four_days_ago, ten_days_from_now]
