from time import sleep

import pytest

from models import PcObject, Provider
from tests.conftest import clean_database, TestClient
from utils.human_ids import humanize
from utils.logger import logger
from tests.test_utils import API_URL, req_with_auth, create_offerer, create_venue, create_user, create_venue_provider, \
    activate_provider, check_open_agenda_api_is_down


@pytest.mark.standalone
class Get:
    class Returns200:
        @clean_database
        def when_venue_provider_exists(self, app):
            # given
            offerer = create_offerer(siren='775671464')
            titelive_things_provider = Provider.getByClassName('TiteLiveThings')
            venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
            venue_provider = create_venue_provider(venue=venue, provider=titelive_things_provider)
            PcObject.save(venue_provider)

            user = create_user()
            PcObject.save(user)
            auth_request = TestClient() \
                .with_auth(email=user.email)
            humanized_venue_provider_id = humanize(venue_provider.id)

            # when
            response = auth_request.get(API_URL + '/venueProviders/' + humanized_venue_provider_id)

            # then
            assert response.status_code == 200

        @clean_database
        def when_listing_all_venues_with_a_valid_venue_id(self, app):
            # given
            offerer = create_offerer(siren='775671464')
            venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
            titelive_things_provider = Provider.getByClassName('TiteLiveThings')
            venue_provider = create_venue_provider(venue=venue, provider=titelive_things_provider)
            PcObject.save(venue_provider)

            user = create_user()
            PcObject.save(user)
            auth_request = TestClient() \
                .with_auth(email=user.email)

            # when
            response = auth_request.get(API_URL + '/venueProviders?venueId=' + humanize(venue.id))

            # then
            assert response.status_code == 200
            logger.info(response.json)
            assert response.json()[0].get('id') == humanize(venue_provider.id)
            assert response.json()[0].get('venueId') == humanize(venue.id)

    class Returns400:
        @clean_database
        def when_listing_all_venues_without_venue_id_argument(self, app):
            # given
            offerer = create_offerer(siren='775671464')
            venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
            titelive_things_provider = Provider.getByClassName('TiteLiveThings')
            venue_provider = create_venue_provider(venue=venue, provider=titelive_things_provider)
            PcObject.save(venue_provider)

            user = create_user()
            PcObject.save(user)
            auth_request = TestClient() \
                .with_auth(email=user.email)

            # when
            response = auth_request.get(API_URL + '/venueProviders')

            # then
            assert response.status_code == 400

    class Returns404:
        @clean_database
        def when_venue_provider_id_does_not_exist(self, app):
            # given
            offerer = create_offerer(siren='775671464')
            venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
            titelive_things_provider = Provider.getByClassName('TiteLiveThings')
            venue_provider = create_venue_provider(venue=venue, provider=titelive_things_provider)
            PcObject.save(venue_provider)

            user = create_user()
            PcObject.save(user)
            auth_request = TestClient() \
                .with_auth(email=user.email)
            non_existing_venue_provider_id = 'ABCDEF'

            # when
            response = auth_request.get(API_URL + '/venueProviders/' + non_existing_venue_provider_id)

            # then
            assert response.status_code == 404


@pytest.mark.standalone
class Delete:
    class Returns200:
        @clean_database
        def when_venue_provider_exists(self, app):
            # given
            offerer = create_offerer(siren='775671464')
            venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
            titelive_things_provider = Provider.getByClassName('TiteLiveThings')
            venue_provider = create_venue_provider(venue=venue, provider=titelive_things_provider)
            PcObject.save(venue_provider)

            user = create_user(is_admin=True, can_book_free_offers=False)
            PcObject.save(user)
            auth_request = TestClient() \
                .with_auth(email=user.email)

            # when
            response = auth_request.delete(API_URL + '/venueProviders/' + humanize(venue_provider.id))

            # then
            assert response.status_code == 200

    class Returns404:
        @clean_database
        def when_venue_provider_does_not_exist(self, app):
            # given
            offerer = create_offerer(siren='775671464')
            venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
            titelive_things_provider = Provider.getByClassName('TiteLiveThings')
            venue_provider = create_venue_provider(venue=venue, provider=titelive_things_provider)
            PcObject.save(venue_provider)

            user = create_user(is_admin=True, can_book_free_offers=False)
            PcObject.save(user)
            auth_request = TestClient() \
                .with_auth(email=user.email)

            # when
            response = auth_request.delete(API_URL + '/venueProviders/ABCDEF')

            # then
            assert response.status_code == 404


@pytest.mark.standalone
class Post:
    class Returns201:
        @clean_database
        @pytest.mark.skipif(check_open_agenda_api_is_down(), reason="Open Agenda API is down")
        def when_venue_provider_exists(self, app):
            # given
            offerer = create_offerer(siren='775671464')
            venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
            PcObject.save(venue)

            provider = activate_provider('OpenAgendaEvents')

            venue_provider_data = {'providerId': humanize(provider.id),
                                   'venueId': humanize(venue.id),
                                   'venueIdAtOfferProvider': '775671464'}
            user = create_user(is_admin=True, can_book_free_offers=False)
            PcObject.save(user)
            auth_request = TestClient() \
                .with_auth(email=user.email)

            # when
            response = auth_request.post(API_URL + '/venueProviders',
                                         json=venue_provider_data)

            # then
            assert response.status_code == 201

            json_response = response.json()
            assert 'id' in json_response
            venue_provider_id = json_response['id']
            assert json_response['lastSyncDate'] is None

            # Test for subprocess result
            read_json = json_response
            tries = 0
            while read_json['lastSyncDate'] is None:
                assert tries < 30
                response_check = req_with_auth(email=user.email)\
                    .get(API_URL + '/venueProviders/' + venue_provider_id)
                assert response_check.status_code == 200
                read_json = response_check.json()
                tries += 1
                sleep(2)


@pytest.mark.standalone
class Patch:
    class Returns200:

        @clean_database
        def when_editing_existing_venue_provider(self, app):
            # given
            offerer = create_offerer(siren='775671464')
            titelive_things_provider = Provider.getByClassName('TiteLiveThings')
            venue = create_venue(offerer, name='Librairie Titelive', siret='77567146400110')
            venue_provider = create_venue_provider(venue=venue, provider=titelive_things_provider)
            PcObject.save(venue_provider)

            user = create_user()
            PcObject.save(user)
            auth_request = TestClient() \
                .with_auth(email=user.email)
            humanized_venue_provider_id = humanize(venue_provider.id)

            # when
            response = auth_request.patch(API_URL + '/venueProviders/' + humanized_venue_provider_id,
                                          json={'venueIdAtOfferProvider': '12345678'})

            # then
            assert response.status_code == 200
            response_check = auth_request.get(API_URL + '/venueProviders/' + humanized_venue_provider_id)
            assert response_check.status_code == 200
            assert response_check.json()['venueIdAtOfferProvider'] == '12345678'
