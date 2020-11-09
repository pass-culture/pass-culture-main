from unittest.mock import patch

import pytest

from pcapi.model_creators.generic_creators import create_offerer
from pcapi.model_creators.generic_creators import create_stock
from pcapi.model_creators.generic_creators import create_user
from pcapi.model_creators.generic_creators import create_user_offerer
from pcapi.model_creators.generic_creators import create_venue
from pcapi.model_creators.specific_creators import create_offer_with_event_product
from pcapi.model_creators.specific_creators import create_offer_with_thing_product
from pcapi.model_creators.specific_creators import create_stock_from_offer
from pcapi.models import Offer
from pcapi.repository import repository
from pcapi.utils.human_ids import humanize

from tests.conftest import TestClient


API_URL = '/venues/'


class Put:
    class Returns401:
        @pytest.mark.usefixtures("db_session")
        def when_the_user_is_not_logged_in(self, app):
            # Given
            user = create_user(email='test@example.net')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            stock = create_stock(offer=offer)
            repository.save(
                stock, user_offerer, venue
            )

            api_url = API_URL + humanize(venue.id) + '/offers/activate'

            # when
            response = TestClient(app.test_client()).put(api_url)

            # then
            assert response.status_code == 401

    class Returns403:
        @pytest.mark.usefixtures("db_session")
        def when_the_user_is_not_venue_managing_offerer(self, app):
            # Given
            user = create_user(email='test@example.net')
            user_with_no_rights = create_user(email='user_with_no_rights@example.net')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            stock = create_stock_from_offer(offer)
            repository.save(
                stock, user_offerer, venue, user_with_no_rights
            )

            api_url = API_URL + humanize(venue.id) + '/offers/activate'

            # When
            response = TestClient(app.test_client()) \
                .with_auth('user_with_no_rights@example.net') \
                .put(api_url)

            # Then
            assert response.status_code == 403

    class Returns404:
        @pytest.mark.usefixtures("db_session")
        def when_the_venue_does_not_exist(self, app):
            # Given
            user = create_user(email='test@example.net')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            offer2 = create_offer_with_thing_product(venue)
            stock1 = create_stock_from_offer(offer)
            offer.isActive = False
            offer2.isActive = False
            repository.save(
                offer2, stock1, user_offerer, venue
            )

            api_url = API_URL + '6TT67RTE/offers/activate'

            # When
            response = TestClient(app.test_client()).with_auth('test@example.net') \
                .put(api_url)

            # Then
            assert response.status_code == 404

    class Returns200:
        @pytest.mark.usefixtures("db_session")
        def when_activating_all_venue_offers(self, app):
            # Given
            user = create_user(email='test@example.net')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            offer2 = create_offer_with_thing_product(venue)
            stock1 = create_stock_from_offer(offer)
            offer.isActive = False
            offer2.isActive = False
            repository.save(
                offer2, stock1, user_offerer, venue
            )

            api_url = API_URL + humanize(venue.id) + '/offers/activate'

            # When
            response = TestClient(app.test_client()) \
                .with_auth('test@example.net') \
                .put(api_url)

            # Then
            assert response.status_code == 200
            assert response.json[0]['isActive'] == True
            assert response.json[1]['isActive'] == True

            offers = Offer.query.all()
            assert offers[0].isActive == True
            assert offers[1].isActive == True

        @patch('pcapi.routes.venues.feature_queries.is_active', return_value=True)
        @patch('pcapi.routes.venues.redis.add_venue_id')
        @pytest.mark.usefixtures("db_session")
        def when_activating_all_venue_offers_expect_venue_id_to_be_added_to_redis(self, mock_redis, mock_feature, app):
            # Given
            user = create_user(email='test@example.net')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            offer2 = create_offer_with_thing_product(venue)
            stock1 = create_stock_from_offer(offer)
            offer.isActive = False
            offer2.isActive = False
            repository.save(
                offer2, stock1, user_offerer, venue
            )

            api_url = API_URL + humanize(venue.id) + '/offers/activate'

            # When
            response = TestClient(app.test_client()) \
                .with_auth('test@example.net') \
                .put(api_url)

            # Then
            assert response.status_code == 200
            mock_redis.assert_called_once_with(client=app.redis_client, venue_id=venue.id)

        @pytest.mark.usefixtures("db_session")
        def when_deactivating_all_venue_offers(self, app):
            # Given
            user = create_user(email='test@example.net')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            offer2 = create_offer_with_thing_product(venue)
            stock1 = create_stock_from_offer(offer)
            repository.save(
                offer2, stock1, user_offerer, venue
            )

            api_url = API_URL + humanize(venue.id) + '/offers/deactivate'

            # When
            response = TestClient(app.test_client()).with_auth('test@example.net') \
                .put(api_url)

            # Then
            assert response.status_code == 200
            assert response.json[0]['isActive'] == False
            assert response.json[1]['isActive'] == False

            offers = Offer.query.all()
            assert not offers[0].isActive
            assert not offers[1].isActive

        @patch('pcapi.routes.venues.feature_queries.is_active', return_value=True)
        @patch('pcapi.routes.venues.redis.add_venue_id')
        @pytest.mark.usefixtures("db_session")
        def when_deactivating_all_venue_offers_expect_venue_id_to_be_added_to_redis(self,
                                                                                    mock_redis,
                                                                                    mock_feature,
                                                                                    app):
            # Given
            user = create_user(email='test@example.net')
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            offer = create_offer_with_event_product(venue)
            offer2 = create_offer_with_thing_product(venue)
            stock1 = create_stock_from_offer(offer)
            repository.save(
                offer2, stock1, user_offerer, venue
            )

            api_url = API_URL + humanize(venue.id) + '/offers/deactivate'

            # When
            response = TestClient(app.test_client()).with_auth('test@example.net') \
                .put(api_url)

            # Then
            assert response.status_code == 200
            mock_redis.assert_called_once_with(client=app.redis_client, venue_id=venue.id)
