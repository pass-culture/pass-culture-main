from unittest.mock import patch

import pytest

from domain.build_recommendations import build_mixed_recommendations
from models import Offer
from tests.test_utils import create_recommendation, create_stock


class MockedOffer(Offer):
    def __init__(self, stocks):
        self._stocks = stocks

    @property
    def stocks(self):
        return self._stocks


@pytest.mark.standalone
def test_build_mixed_recommendations_with_only_created_recommendations():
    # given
    created_recommendations = [create_recommendation(idx=1), create_recommendation(idx=2)]
    read_recommendations = []
    unread_recommendations = []

    # when
    created_recommendations = build_mixed_recommendations(created_recommendations, read_recommendations,
                                                          unread_recommendations)

    # then
    assert [r.id for r in created_recommendations] == [1, 2]


@pytest.mark.standalone
def test_build_mixed_recommendations_with_created_recommendations_and_unread_but_none_read():
    # given
    created_recommendations = [create_recommendation(idx=1), create_recommendation(idx=2)]
    read_recommendations = []
    unread_recommendations = [create_recommendation(idx=3), create_recommendation(idx=4)]

    # when
    created_recommendations = build_mixed_recommendations(created_recommendations, read_recommendations,
                                                          unread_recommendations)

    # then
    assert [r.id for r in created_recommendations] == [1, 2, 3, 4]


@pytest.mark.standalone
def test_build_mixed_recommendations_with_created_recommendations_and_read_but_none_unread():
    # given
    created_recommendations = [create_recommendation(idx=1), create_recommendation(idx=2)]
    read_recommendations = [create_recommendation(idx=3), create_recommendation(idx=4)]
    unread_recommendations = []

    # when
    created_recommendations = build_mixed_recommendations(created_recommendations, read_recommendations,
                                                          unread_recommendations)

    # then
    assert [r.id for r in created_recommendations] == [1, 2, 3, 4]


@pytest.mark.standalone
def test_build_mixed_recommendations_with_only_read_recommendations_and_none_created():
    # given
    created_recommendations = []
    read_recommendations = [create_recommendation(idx=1), create_recommendation(idx=2)]
    unread_recommendations = []

    # when
    created_recommendations = build_mixed_recommendations(created_recommendations, read_recommendations,
                                                          unread_recommendations)

    # then
    assert [r.id for r in created_recommendations] == [1, 2]


@pytest.mark.standalone
def test_build_mixed_recommendations_with_only_unread_recommendations_and_none_created():
    # given
    created_recommendations = []
    read_recommendations = []
    unread_recommendations = [create_recommendation(idx=1), create_recommendation(idx=2)]

    # when
    created_recommendations = build_mixed_recommendations(created_recommendations, read_recommendations,
                                                          unread_recommendations)

    # then
    assert [r.id for r in created_recommendations] == [1, 2]


@pytest.mark.standalone
def test_build_mixed_recommendations_with_read_recommendations_and_unread_but_none_created():
    # given
    created_recommendations = []
    read_recommendations = [create_recommendation(idx=1), create_recommendation(idx=2)]
    unread_recommendations = [create_recommendation(idx=3), create_recommendation(idx=4)]

    # when
    created_recommendations = build_mixed_recommendations(created_recommendations, read_recommendations,
                                                          unread_recommendations)

    # then
    assert [r.id for r in created_recommendations] == [3, 4, 1, 2]


@pytest.mark.standalone
def test_build_mixed_recommendations_with_all_sorts_of_recommendations():
    # given
    created_recommendations = [create_recommendation(idx=5), create_recommendation(idx=6)]
    read_recommendations = [create_recommendation(idx=1), create_recommendation(idx=2)]
    unread_recommendations = [create_recommendation(idx=3), create_recommendation(idx=4)]

    # when
    created_recommendations = build_mixed_recommendations(created_recommendations, read_recommendations,
                                                          unread_recommendations)

    # then
    assert [r.id for r in created_recommendations] == [5, 6, 3, 4, 1, 2]


@pytest.mark.standalone
@patch('domain.build_recommendations.feature_paid_offers_enabled', return_value=False)
def test_build_mixed_recommendations_removes_the_recommendations_on_paid_offers_if_feature_is_disabled(feature_enabled):
    # given

    paid_stock = create_stock(price=10)
    free_stock = create_stock(price=0)
    offer_with_paid_stock = MockedOffer([paid_stock, free_stock])
    offer_with_free_stock = MockedOffer([free_stock])

    created_recommendations = [create_recommendation(offer=offer_with_paid_stock, idx=5),
                               create_recommendation(offer=offer_with_free_stock, idx=6)]
    read_recommendations = [create_recommendation(offer=offer_with_free_stock, idx=1),
                            create_recommendation(offer=offer_with_free_stock, idx=2)]
    unread_recommendations = [create_recommendation(offer=offer_with_paid_stock, idx=3),
                              create_recommendation(offer=offer_with_paid_stock, idx=4)]

    # when
    created_recommendations = build_mixed_recommendations(created_recommendations, read_recommendations,
                                                          unread_recommendations)

    # then
    assert [r.id for r in created_recommendations] == [6, 1, 2]
