import pytest

from models import PcObject
from tests.conftest import clean_database, TestClient
from tests.test_utils import API_URL, \
    create_offer_with_event_product, \
    create_offerer, \
    create_recommendation, \
    create_user, \
    create_venue

RECOMMENDATION_URL = API_URL + '/recommendations'


class Get:
    class Returns401:
        @clean_database
        def when_not_logged_in(self, app):
            # when
            response = TestClient().get(RECOMMENDATION_URL + '/favorites')

            # then
            assert response.status_code == 401

    class Returns200:
        @clean_database
        def when_current_user_has_favorites(self, app):
            # given
            user1 = create_user(email='user1@test.com')
            user2 = create_user(email='user2@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer1 = create_offer_with_event_product(venue)
            offer2 = create_offer_with_event_product(venue)
            recommendation1 = create_recommendation(offer1, user1, is_favorite=False)
            recommendation2 = create_recommendation(offer2, user1, is_favorite=True)
            recommendation3 = create_recommendation(offer2, user1, is_favorite=True)
            recommendation4 = create_recommendation(offer2, user2, is_favorite=True)
            PcObject.save(user1, user2, recommendation1, recommendation2, recommendation3, recommendation4)

            # when
            response = TestClient().with_auth(user1.email) \
                .get(RECOMMENDATION_URL + '/favorites')

            # then
            assert response.status_code == 200
            assert len(response.json()) == 2

        @clean_database
        def when_current_user_has_no_favorites(self, app):
            # given
            user1 = create_user(email='user1@test.com')
            user2 = create_user(email='user2@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            offer1 = create_offer_with_event_product(venue)
            recommendation1 = create_recommendation(offer1, user1, is_favorite=False)
            PcObject.save(user1, user2, recommendation1)

            # when
            response = TestClient().with_auth(user1.email) \
                .get(RECOMMENDATION_URL + '/favorites')

            # then
            assert response.status_code == 200
            assert len(response.json()) == 0
