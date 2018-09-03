import pytest

from models import PcObject
from repository.recommendation_queries import filter_out_recommendation_on_soft_deleted_stocks
from tests.conftest import clean_database
from utils.test_utils import create_recommendation, create_event_offer, create_offerer, \
    create_venue, create_user, create_stock_from_event_occurrence, create_event_occurrence, create_stock_from_offer, \
    create_thing_offer


@clean_database
@pytest.mark.standalone
def test_query_with_union_all(app):
    # Given
    offerer = create_offerer()
    venue = create_venue(offerer)
    offer = create_event_offer(venue)
    user = create_user()
    event_occurrence1 = create_event_occurrence(offer)
    event_occurrence2 = create_event_occurrence(offer)
    stock1 = create_stock_from_event_occurrence(offerer, event_occurrence1)
    stock2 = create_stock_from_event_occurrence(offerer, event_occurrence2)
    thing_offer1 = create_thing_offer(venue)
    thing_offer2 = create_thing_offer(venue)
    stock3 = create_stock_from_offer(offerer, thing_offer1)
    stock4 = create_stock_from_offer(offerer, thing_offer2)
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
