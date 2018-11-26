from datetime import datetime, timedelta

import pytest

from models import PcObject, Recommendation
from repository.recommendation_queries import filter_out_recommendation_on_soft_deleted_stocks, \
    filter_unseen_valid_recommendations_for_user
from tests.conftest import clean_database
from utils.test_utils import create_recommendation, create_event_offer, create_offerer, \
    create_venue, create_user, create_stock_from_event_occurrence, create_event_occurrence, create_stock_from_offer, \
    create_thing_offer, create_mediation


@clean_database
@pytest.mark.standalone
def test_filter_out_recommendation_on_soft_deleted_stocks_returns_recos_with_at_least_one_not_soft_deleted_stock(app):
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
    stock1.isSoftDeleted = True
    stock3.isSoftDeleted = True
    recommendation1 = create_recommendation(offer, user)
    recommendation2 = create_recommendation(thing_offer1, user)
    recommendation3 = create_recommendation(thing_offer2, user)
    PcObject.check_and_save(stock1, stock2, stock3, stock4, recommendation1, recommendation2, recommendation3)

    # When
    result = filter_out_recommendation_on_soft_deleted_stocks().all()

    # Then
    recommendation_ids = [r.id for r in result]
    assert recommendation1.id in recommendation_ids
    assert recommendation2.id not in recommendation_ids
    assert recommendation3.id in recommendation_ids
    

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

    PcObject.check_and_save(invalid_recommendation, valid_recommendation, recommendation_with_no_validity_date, tuto_recommendation)

    query = Recommendation.query

    # When
    recommendation_query = filter_unseen_valid_recommendations_for_user(query, user, seen_recommendation_ids=[])
    # Then
    recommendations = recommendation_query.all()
    assert len(recommendations) == 2
    assert valid_recommendation in recommendations
    assert recommendation_with_no_validity_date in recommendations