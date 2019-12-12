from decimal import Decimal
from unittest.mock import patch

from models import PcObject, ApiErrors, VenueProvider, VenueProviderPriceRule
from tests.conftest import clean_database, TestClient
from tests.test_utils import create_offerer, create_venue, create_user, activate_provider, \
    create_venue_provider
from utils.config import API_ROOT_PATH
from utils.human_ids import humanize, dehumanize


class Post:
    class Returns201:
        @clean_database
        @patch('routes.venue_providers.subprocess.Popen')
        def when_venue_provider_exists(self, mock_suprocess, app):
            # Given
            user = create_user(is_admin=True, can_book_free_offers=False)
            offerer = create_offerer(siren='775671464')
            venue = create_venue(offerer, name='Librairie Titelive')
            PcObject.save(venue, user)

            provider = activate_provider('TiteLiveStocks')

            venue_provider_data = {
                'providerId': humanize(provider.id),
                'venueId': humanize(venue.id),
                'venueIdAtOfferProvider': '77567146400110'
            }

            auth_request = TestClient(app.test_client()) \
                .with_auth(email=user.email)

            # When
            response = auth_request.post('/venueProviders',
                                         json=venue_provider_data)

            # Then
            assert response.status_code == 201
            assert 'id' in response.json
            venue_provider_id = response.json['id']
            mock_suprocess.assert_called_once_with('PYTHONPATH="." python scripts/pc.py update_providables'
                                                   + f' --venue-provider-id {dehumanize(venue_provider_id)}',
                                                   cwd=API_ROOT_PATH,
                                                   shell=True)

        @clean_database
        @patch('routes.venue_providers.subprocess.Popen')
        def when_add_allocine_stocks_provider_with_price(self, mock_suprocess, app):
            # Given
            offerer = create_offerer(siren='775671464')
            venue = create_venue(offerer, name='Cinema Allocine')
            user = create_user(is_admin=True, can_book_free_offers=False)
            PcObject.save(venue, user)

            provider = activate_provider('AllocineStocks')

            venue_provider_data = {
                'providerId': humanize(provider.id),
                'venueId': humanize(venue.id),
                'venueIdAtOfferProvider': '77567146400110',
                'price': '9.99'
            }

            auth_request = TestClient(app.test_client()) \
                .with_auth(email=user.email)

            # When
            response = auth_request.post('/venueProviders',
                                         json=venue_provider_data)

            # Then
            assert response.status_code == 201
            venue_provider = VenueProvider.query.one()
            venue_provider_price_rule = VenueProviderPriceRule.query.one()
            assert len(venue_provider.priceRules) == 1
            assert venue_provider_price_rule.price == Decimal('9.99')

    class Returns400:
        @clean_database
        @patch('routes.venue_providers.validate_new_venue_provider_information')
        def when_api_error_raise_from_payload_validation(self, validate_new_venue_provider_information, app):
            # Given
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
                'venueIdAtOfferProvider': '77567146400110',
            }

            # When
            response = auth_request.post('/venueProviders', json=venue_provider_data)

            # Then
            assert response.status_code == 400
            assert ['error received'] == response.json['errors']

        @clean_database
        def when_trying_to_add_existing_provider(self, app):
            # Given
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
                'venueIdAtOfferProvider': '1234567'
            }

            # When
            response = auth_request.post('/venueProviders', json=venue_provider_data)

            # Then
            assert response.status_code == 400
            assert response.json['global'] == ["Votre lieu est déjà lié à cette source"]

        @clean_database
        @patch('routes.venue_providers.subprocess.Popen')
        def when_add_allocine_stocks_provider_with_wrong_format_price(self, mock_suprocess, app):
            # Given
            offerer = create_offerer(siren='775671464')
            venue = create_venue(offerer, name='Cinema Allocine')
            user = create_user(is_admin=True, can_book_free_offers=False)
            PcObject.save(venue, user)

            provider = activate_provider('AllocineStocks')

            venue_provider_data = {
                'providerId': humanize(provider.id),
                'venueId': humanize(venue.id),
                'venueIdAtOfferProvider': '77567146400110',
                'price': 'wrong_price'
            }

            auth_request = TestClient(app.test_client()) \
                .with_auth(email=user.email)

            # When
            response = auth_request.post('/venueProviders',
                                         json=venue_provider_data)

            # Then
            assert response.status_code == 400
            assert response.json['global'] == ["Le prix doit être un nombre décimal"]
