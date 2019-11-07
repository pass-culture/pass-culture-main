from unittest.mock import patch

import pytest

from models import PcObject, ApiErrors
from tests.conftest import clean_database, TestClient
from tests.test_utils import create_offerer, create_venue, create_user, activate_provider, \
    check_titelive_stocks_api_is_down, create_product_with_thing_type, create_venue_provider
from utils.human_ids import humanize


class Post:
    class Returns201:
        @clean_database
        @pytest.mark.skipif(check_titelive_stocks_api_is_down(), reason="TiteLiveStocks API is down")
        def when_venue_provider_exists(self, app):
            # given
            offerer = create_offerer(siren='775671464')
            venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
            PcObject.save(venue)

            provider = activate_provider('TiteLiveStocks')
            product = create_product_with_thing_type(id_at_providers='0002730757438')

            venue_provider_data = {'providerId': humanize(provider.id),
                                   'venueId': humanize(venue.id),
                                   'venueIdAtOfferProvider': '77567146400110'}
            user = create_user(is_admin=True, can_book_free_offers=False)
            PcObject.save(product, user)
            auth_request = TestClient(app.test_client()) \
                .with_auth(email=user.email)

            # when
            response = auth_request.post('/venueProviders',
                                         json=venue_provider_data)

            # then
            assert response.status_code == 201

            json_response = response.json
            assert 'id' in json_response
            venue_provider_id = json_response['id']
            assert json_response['lastSyncDate'] is None

    class Returns400:
        @clean_database
        @patch('routes.venue_providers.validate_new_venue_provider_information')
        def when_api_error_raise_from_payload_validation(self, validate_new_venue_provider_information, app):
            # given
            api_errors = ApiErrors()
            api_errors.status_code = 400
            api_errors.add_error('errors', 'error received')

            validate_new_venue_provider_information.side_effect = api_errors

            user = create_user(is_admin=True, can_book_free_offers=False)
            PcObject.save(user)
            auth_request = TestClient(app.test_client()) \
                .with_auth(email=user.email)
            venue_provider_data = {
                'providerId': 'B9',
                'venueId': 'B9',
                'venueIdAtOfferProvider': '77567146400110'
            }

            # when
            response = auth_request.post('/venueProviders', json=venue_provider_data)

            # then
            assert response.status_code == 400
            assert ['error received'] == response.json['errors']

        @clean_database
        def when_trying_to_add_existing_provider(self, app):
            # given
            user = create_user(is_admin=True, can_book_free_offers=False)
            offerer = create_offerer()
            venue = create_venue(offerer)
            provider = activate_provider('TiteLiveStocks')
            venue_provider = create_venue_provider(venue, provider, venue_id_at_offer_provider='1234567')
            PcObject.save(user, venue_provider)

            auth_request = TestClient(app.test_client()) \
                .with_auth(email=user.email)
            venue_provider_data = {
                'providerId': humanize(provider.id),
                'venueId': humanize(venue.id),
                'venueIdAtOfferProvider': '0987654321'
            }

            # when
            response = auth_request.post('/venueProviders', json=venue_provider_data)

            # then
            assert response.status_code == 400
            assert response.json['global'] == ["Votre lieu est déjà lié à cette source"]
