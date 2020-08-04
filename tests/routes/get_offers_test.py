import secrets
from unittest.mock import patch

from domain.pro_offers.paginated_offers import PaginatedOffers
from repository import repository
from tests.conftest import clean_database, TestClient
from tests.model_creators.generic_creators import create_user, create_offerer, create_venue, create_user_offerer
from tests.model_creators.specific_creators import create_offer_with_thing_product
from use_cases.list_offers_for_pro_user import OffersRequestParameters
from utils.human_ids import humanize


class Get:
    class Returns200:
        @clean_database
        def when_user_is_admin_and_request_specific_venue(self, app):
            # Given
            admin = create_user(is_admin=True, can_book_free_offers=False)
            offerer = create_offerer()
            venue = create_venue(offerer)
            repository.save(admin, venue)

            # when
            response = TestClient(app.test_client()) \
                .with_auth(email=admin.email).get(f'/offers?venueId={humanize(venue.id)}')

            # then
            assert response.status_code == 200

        @clean_database
        @patch('routes.offers.list_offers_for_pro_user.execute')
        def test_results_are_paginated_with_count_in_headers(self, list_offers_mock, app):
            # Given
            user = create_user()
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            offer1 = create_offer_with_thing_product(venue)
            offer2 = create_offer_with_thing_product(venue)
            repository.save(user_offerer, offer1, offer2)
            list_offers_mock.return_value = PaginatedOffers(offers=[offer1], total=2)

            # when
            response = TestClient(app.test_client()) \
                .with_auth(email=user.email).get('/offers?paginate=1')

            # then
            offers = response.json
            assert response.status_code == 200
            assert len(offers) == 1
            assert response.headers['Total-Data-Count'] == "2"

        @clean_database
        @patch('routes.offers.list_offers_for_pro_user.execute')
        def test_does_not_show_result_to_user_offerer_when_not_validated(self, list_offers_mock, app):
            # given
            user = create_user()
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer, validation_token=secrets.token_urlsafe(20))
            venue = create_venue(offerer)
            offer = create_offer_with_thing_product(venue)
            repository.save(user_offerer, offer)
            list_offers_mock.return_value = PaginatedOffers(offers=[], total=0)

            # when
            response = TestClient(app.test_client()).with_auth(email=user.email).get('/offers')

            # then
            assert response.status_code == 200
            assert response.json == []

        @clean_database
        @patch('routes.offers.list_offers_for_pro_user.execute')
        def test_results_are_filtered_by_given_venue_id(self, list_offers_mock, app):
            # given
            user = create_user()
            offerer = create_offerer()
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer)
            repository.save(user_offerer, venue)

            # when
            response = TestClient(app.test_client()) \
                .with_auth(email=user.email).get('/offers?venueId=' + humanize(venue.id))

            # then
            assert response.status_code == 200
            list_offers_mock.assert_called_once()
            expected_parameter = list_offers_mock.call_args[0][0]
            assert isinstance(expected_parameter, OffersRequestParameters)
            assert expected_parameter.user_id == user.id
            assert expected_parameter.user_is_admin == user.isAdmin
            assert expected_parameter.offerer_id == None
            assert expected_parameter.venue_id == venue.id
            assert expected_parameter.pagination_limit == 10
            assert expected_parameter.keywords == None
            assert expected_parameter.page == 0

    class Returns404:
        @clean_database
        def when_requested_venue_does_not_exist(self, app):
            # Given
            user = create_user(email='user@test.com')
            repository.save(user)

            # when
            response = TestClient(app.test_client()) \
                .with_auth(email=user.email).get('/offers?venueId=ABC')

            # then
            assert response.status_code == 404
            assert response.json == {'global': ["La page que vous recherchez n'existe pas"]}

    class Returns403:
        @clean_database
        def when_user_has_no_rights_on_requested_venue(self, app):
            # Given
            user = create_user(email='user@test.com')
            offerer = create_offerer()
            venue = create_venue(offerer)
            repository.save(user, venue)

            # when
            response = TestClient(app.test_client()) \
                .with_auth(email=user.email).get(f'/offers?venueId={humanize(venue.id)}')

            # then
            assert response.status_code == 403
            assert response.json == {
                'global': ["Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."]}
