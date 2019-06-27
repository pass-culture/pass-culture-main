from time import sleep

import pytest

from models import PcObject, Provider
from tests.conftest import clean_database, TestClient
from tests.test_utils import API_URL, create_offerer, create_venue, create_user, activate_provider, \
    check_titelive_stocks_api_is_down, create_user_offerer, create_venue_provider, create_product_with_Thing_type
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
            product = create_product_with_Thing_type(id_at_providers='0002730757438')

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


    class Returns404:
        @clean_database
        def when_provider_id_does_not_exist(self, app):
            # given
            offerer = create_offerer()
            user = create_user()
            user_offerer = create_user_offerer(user, offerer, is_admin=True)
            venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
            PcObject.save(user_offerer, venue)

            auth_request = TestClient(app.test_client()) \
                .with_auth(email=user.email)
            venue_provider_data = {'providerId': "AZEFGRZ5",
                                   'venueId': humanize(venue.id),
                                   'venueIdAtOfferProvider': '775671464'}

            # when
            response = auth_request.post(API_URL + '/venueProviders',
                                         json=venue_provider_data)

            # then
            assert response.status_code == 404

    class Returns401:
        @clean_database
        def when_provider_is_not_active_and_enabled_for_pro_property_is_true(self, app):
            # given
            provider = Provider()
            provider.name = 'Open Agenda'
            provider.localClass = 'OpenAgenda'
            provider.isActive = False
            provider.enabledForPro = True
            offerer = create_offerer()
            user = create_user()
            user_offerer = create_user_offerer(user, offerer, is_admin=True)
            venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
            PcObject.save(provider, user_offerer, venue)

            auth_request = TestClient(app.test_client()) \
                .with_auth(email=user.email)
            venue_provider_data = {'providerId': humanize(provider.id),
                                   'venueId': humanize(venue.id),
                                   'venueIdAtOfferProvider': '775671464'}

            # when
            response = auth_request.post(API_URL + '/venueProviders',
                                         json=venue_provider_data)

            # then
            assert response.status_code == 401
            assert response.json['localClass'] == ["Ce fournisseur n'est pas activé"]

        @clean_database
        def when_provider_is_not_active_and_enabled_for_pro_property_is_not_active(self, app):
            # given
            provider = Provider()
            provider.name = 'Open Agenda'
            provider.localClass = 'OpenAgenda'
            provider.isActive = False
            provider.enabledForPro = False
            offerer = create_offerer()
            user = create_user()
            user_offerer = create_user_offerer(user, offerer, is_admin=True)
            venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
            PcObject.save(provider, user_offerer, venue)

            auth_request = TestClient(app.test_client()) \
                .with_auth(email=user.email)
            venue_provider_data = {'providerId': humanize(provider.id),
                                   'venueId': humanize(venue.id),
                                   'venueIdAtOfferProvider': '775671464'}

            # when
            response = auth_request.post(API_URL + '/venueProviders',
                                         json=venue_provider_data)

            # then
            assert response.status_code == 401
            assert response.json['localClass'] == ["Ce fournisseur n'est pas activé"]

        @clean_database
        def when_venue_provider_with_same_identifier_already_exists(self, app):
            # given
            provider = Provider()
            provider.name = 'Open Agenda'
            provider.localClass = 'OpenAgenda'
            provider.isActive = True
            provider.enabledForPro = True
            offerer = create_offerer()
            user = create_user()
            user_offerer = create_user_offerer(user, offerer, is_admin=True)
            venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
            venue_provider = create_venue_provider(venue, provider, venue_id_at_offer_provider="775671464")
            PcObject.save(provider, user_offerer, venue, venue_provider)

            auth_request = TestClient(app.test_client()) \
                .with_auth(email=user.email)
            venue_provider_data = {'providerId': humanize(provider.id),
                                   'venueId': humanize(venue.id),
                                   'venueIdAtOfferProvider': '775671464'}

            # when
            response = auth_request.post(API_URL + '/venueProviders',
                                         json=venue_provider_data)

            # then
            assert response.status_code == 401
            assert response.json['venueIdAtOfferProvider'] == ["Il y a déjà un fournisseur pour votre identifiant"]
