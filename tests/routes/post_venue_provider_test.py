import pytest

from models import PcObject, Provider
from tests.conftest import clean_database, TestClient
from tests.test_utils import API_URL, create_offerer, create_venue, create_user, activate_provider, \
    check_titelive_stocks_api_is_down, create_user_offerer, create_venue_provider, create_product_with_thing_type
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
