import pytest
from datetime import datetime, timedelta

from models import PcObject, Recommendation
from repository.recommendation_queries import keep_only_bookable_stocks, \
    filter_unseen_valid_recommendations_for_user, \
    update_read_recommendations
from tests.conftest import clean_database
from utils.human_ids import humanize
from utils.test_utils import create_recommendation, create_event_offer, create_offerer, \
    create_venue, create_user, create_stock_from_event_occurrence, create_event_occurrence, create_stock_from_offer, \
    create_thing_offer, create_mediation


@clean_database
@pytest.mark.standalone
def test_filter_out_recommendation_with_not_bookable_stocks_returns_recos_with_at_least_one_not_soft_deleted_stock(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer)
    user = create_user()

    event_offer = create_event_offer(venue)
    soft_deleted_thing_offer = create_thing_offer(venue)
    active_thing_offer = create_thing_offer(venue)

    event_occurrence1 = create_event_occurrence(event_offer)
    event_occurrence2 = create_event_occurrence(event_offer)

    active_thing_stock = create_stock_from_offer(active_thing_offer)
    active_event_stock = create_stock_from_event_occurrence(event_occurrence2)
    soft_deleted_event_stock = create_stock_from_event_occurrence(event_occurrence1)
    soft_deleted_event_stock.isSoftDeleted = True
    soft_deleted_thing_stock = create_stock_from_offer(soft_deleted_thing_offer)
    soft_deleted_thing_stock.isSoftDeleted = True

    recommendation_on_active_thing_stock = create_recommendation(active_thing_offer, user)
    recommendation_on_both_soft_deleted_and_active_event_stocks = create_recommendation(event_offer, user)
    recommendation_on_soft_deleted_thing_stock = create_recommendation(soft_deleted_thing_offer, user)

    PcObject.check_and_save(soft_deleted_event_stock, active_event_stock, soft_deleted_thing_stock, active_thing_stock,
                            recommendation_on_both_soft_deleted_and_active_event_stocks,
                            recommendation_on_soft_deleted_thing_stock, recommendation_on_active_thing_stock)

    # When
    result = keep_only_bookable_stocks().all()

    # Then
    recommendation_ids = [r.id for r in result]
    assert recommendation_on_both_soft_deleted_and_active_event_stocks.id in recommendation_ids
    assert recommendation_on_soft_deleted_thing_stock.id not in recommendation_ids
    assert recommendation_on_active_thing_stock.id in recommendation_ids


@clean_database
@pytest.mark.standalone
def test_filter_out_recommendation_with_not_bookable_stocks_returns_recos_with_valid_booking_date(app):
    # Given
    one_day_ago = datetime.utcnow() - timedelta(days=1)
    tomorrow = datetime.utcnow() + timedelta(days=1)

    offerer = create_offerer()
    venue = create_venue(offerer)
    user = create_user()

    invalid_booking_date_offer = create_thing_offer(venue)
    valid_booking_date_offer = create_thing_offer(venue)

    invalid_booking_date_stock = create_stock_from_offer(invalid_booking_date_offer, booking_limit_datetime=one_day_ago)
    valid_booking_date_stock_valid = create_stock_from_offer(valid_booking_date_offer, booking_limit_datetime=tomorrow)
    valid_booking_date_stock_invalid = create_stock_from_offer(valid_booking_date_offer, booking_limit_datetime=one_day_ago)

    recommendation_on_invalid_booking_date_stock = create_recommendation(invalid_booking_date_offer, user)
    recommendation_on_valid_booking_date_stock = create_recommendation(valid_booking_date_offer, user)

    PcObject.check_and_save(invalid_booking_date_stock, recommendation_on_invalid_booking_date_stock, recommendation_on_valid_booking_date_stock, valid_booking_date_stock_valid, valid_booking_date_stock_invalid)

    # When
    result = keep_only_bookable_stocks().all()

    # Then
    recommendation_ids = [r.id for r in result]
    assert len(recommendation_ids) == 1
    assert recommendation_on_valid_booking_date_stock.id in recommendation_ids


@pytest.mark.standalone
@clean_database
def test_filter_unseen_valid_recommendations_for_user_only_keeps_non_tuto_recommendations_that_have_not_expired(app):
    # Given
    now = datetime.utcnow()
    five_minutes_ago = now - timedelta(minutes=5)
    tomorrow = now + timedelta(days=1)

    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_thing_offer(venue)
    user = create_user()
    mediation = create_mediation(offer)
    tuto_mediation = create_mediation(offer, tuto_index=1)
    invalid_recommendation = create_recommendation(offer, user, mediation, valid_until_date=five_minutes_ago)
    recommendation_with_no_validity_date = create_recommendation(offer, user, mediation, valid_until_date=None)
    valid_recommendation = create_recommendation(offer, user, mediation, valid_until_date=tomorrow)
    tuto_recommendation = create_recommendation(offer, user, tuto_mediation, valid_until_date=None)

    PcObject.check_and_save(invalid_recommendation, valid_recommendation, recommendation_with_no_validity_date,
                            tuto_recommendation)

    query = Recommendation.query

    # When
    recommendation_query = filter_unseen_valid_recommendations_for_user(query, user, seen_recommendation_ids=[])
    # Then
    recommendations = recommendation_query.all()
    assert len(recommendations) == 2
    assert valid_recommendation in recommendations
    assert recommendation_with_no_validity_date in recommendations


@pytest.mark.standalone
@clean_database
def test_update_read_recommendations(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_event_offer(venue)
    user = create_user()
    event_occurrence1 = create_event_occurrence(offer)
    event_occurrence2 = create_event_occurrence(offer)
    stock1 = create_stock_from_event_occurrence(event_occurrence1)
    stock2 = create_stock_from_event_occurrence(event_occurrence2)
    thing_offer1 = create_thing_offer(venue)
    thing_offer2 = create_thing_offer(venue)
    stock3 = create_stock_from_offer(thing_offer1)
    stock4 = create_stock_from_offer(thing_offer2)
    recommendation1 = create_recommendation(offer, user)
    recommendation2 = create_recommendation(thing_offer1, user)
    recommendation3 = create_recommendation(thing_offer2, user)
    PcObject.check_and_save(stock1, stock2, stock3, stock4, recommendation1, recommendation2, recommendation3)

    # When
    reads = [
        {"id": humanize(recommendation1.id), "dateRead": "2018-12-17T15:59:11.689Z"},
        {"id": humanize(recommendation2.id), "dateRead": "2018-12-17T15:59:15.689Z"},
        {"id": humanize(recommendation3.id), "dateRead": "2018-12-17T15:59:21.689Z"},
    ]
    update_read_recommendations(reads)

    # Then
    assert recommendation1.dateRead == datetime(2018, 12, 17, 15, 59, 11, 689000)
    assert recommendation2.dateRead == datetime(2018, 12, 17, 15, 59, 15, 689000)
    assert recommendation3.dateRead == datetime(2018, 12, 17, 15, 59, 21, 689000)
