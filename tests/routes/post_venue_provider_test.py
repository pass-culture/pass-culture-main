from decimal import Decimal
from unittest.mock import patch

from models import ApiErrors, VenueProvider, VenueProviderPriceRule
from repository.repository import Repository
from tests.conftest import clean_database, TestClient
from tests.model_creators.generic_creators import create_user, create_offerer, create_venue, create_venue_provider
from tests.model_creators.provider_creators import activate_provider
from utils.config import API_ROOT_PATH
from utils.human_ids import humanize, dehumanize


class Post:
    class Returns201:
        @clean_database
        @patch('routes.venue_providers.subprocess.Popen')
        def when_venue_provider_is_successfully_created(self, mock_subprocess, app):
            # Given
            user = create_user(is_admin=True, can_book_free_offers=False)
            offerer = create_offerer()
            venue = create_venue(offerer, siret='12345678912345')
            Repository.save(venue, user)

            provider = activate_provider('TiteLiveStocks')

            venue_provider_data = {
                'providerId': humanize(provider.id),
                'venueId': humanize(venue.id),
            }

            auth_request = TestClient(app.test_client()) \
                .with_auth(email=user.email)

            # When
            response = auth_request.post('/venueProviders',
                                         json=venue_provider_data)

            # Then
            assert response.status_code == 201
            venue_provider = VenueProvider.query.one()
            assert venue_provider.venueId == venue.id
            assert venue_provider.providerId == provider.id
            assert venue_provider.venueIdAtOfferProvider == '12345678912345'
            assert 'id' in response.json
            venue_provider_id = response.json['id']
            mock_subprocess.assert_called_once_with('PYTHONPATH="." python scripts/pc.py update_providables'
                                                    + f' --venue-provider-id {dehumanize(venue_provider_id)}',
                                                    cwd=API_ROOT_PATH,
                                                    shell=True)

        @clean_database
        @patch('routes.venue_providers.subprocess.Popen')
        def when_add_allocine_stocks_provider_with_price(self, mock_subprocess, app):
            # Given
            offerer = create_offerer(siren='775671464')
            venue = create_venue(offerer)
            user = create_user(is_admin=True, can_book_free_offers=False)
            Repository.save(venue, user)

            provider = activate_provider('AllocineStocks')

            venue_provider_data = {
                'providerId': humanize(provider.id),
                'venueId': humanize(venue.id),
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

            user = create_user(can_book_free_offers=False, is_admin=True)
            Repository.save(user)
            auth_request = TestClient(app.test_client()) \
                .with_auth(email=user.email)
            venue_provider_data = {
                'providerId': 'B9',
                'venueId': 'B9',
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
            venue = create_venue(offerer, siret='12345678912345')
            provider = activate_provider('TiteLiveStocks')
            venue_provider = create_venue_provider(venue, provider, venue_id_at_offer_provider='12345678912345')
            Repository.save(user, venue_provider)

            auth_request = TestClient(app.test_client()) \
                .with_auth(email=user.email)
            venue_provider_data = {
                'providerId': humanize(provider.id),
                'venueId': humanize(venue.id),
            }

            # When
            response = auth_request.post('/venueProviders', json=venue_provider_data)

            # Then
            assert response.status_code == 400
            assert response.json['global'] == ["Votre lieu est déjà lié à cette source"]

        @clean_database
        @patch('routes.venue_providers.subprocess.Popen')
        def when_add_allocine_stocks_provider_with_wrong_format_price(self, mock_subprocess, app):
            # Given
            offerer = create_offerer(siren='775671464')
            venue = create_venue(offerer)
            user = create_user(is_admin=True, can_book_free_offers=False)
            Repository.save(venue, user)

            provider = activate_provider('AllocineStocks')

            venue_provider_data = {
                'providerId': humanize(provider.id),
                'venueId': humanize(venue.id),
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
            assert VenueProvider.query.count() == 0

        @clean_database
        @patch('routes.venue_providers.subprocess.Popen')
        def when_add_allocine_stocks_provider_with_no_price(self, mock_subprocess, app):
            # Given
            offerer = create_offerer(siren='775671464')
            venue = create_venue(offerer)
            user = create_user(is_admin=True, can_book_free_offers=False)
            Repository.save(venue, user)

            provider = activate_provider('AllocineStocks')

            venue_provider_data = {
                'providerId': humanize(provider.id),
                'venueId': humanize(venue.id),
            }

            auth_request = TestClient(app.test_client()) \
                .with_auth(email=user.email)

            # When
            response = auth_request.post('/venueProviders',
                                         json=venue_provider_data)

            # Then
            assert response.status_code == 400
            assert response.json['price'] == ["Cette information est obligatoire"]
            assert VenueProvider.query.count() == 0

    class Returns401:
        @clean_database
        def when_user_is_not_logged_in(self, app):
            # when
            response = TestClient(app.test_client()).post('/venueProviders')

            # then
            assert response.status_code == 401

    class Returns404:
        @clean_database
        def when_venue_does_not_exist(self, app):
            # Given
            user = create_user(is_admin=True, can_book_free_offers=False)
            offerer = create_offerer(siren='775671464')
            venue = create_venue(offerer)
            Repository.save(venue, user)

            provider = activate_provider('TiteLiveStocks')

            venue_provider_data = {
                'providerId': humanize(provider.id),
                'venueId': 'AZERT',
            }

            auth_request = TestClient(app.test_client()) \
                .with_auth(email=user.email)

            # When
            response = auth_request.post('/venueProviders',
                                         json=venue_provider_data)

            # Then
            assert response.status_code == 404
