from time import sleep

import pytest

from models import PcObject
from tests.conftest import clean_database, TestClient
from tests.test_utils import API_URL, req_with_auth, create_offerer, create_venue, create_user, activate_provider, \
    check_open_agenda_api_is_down
from utils.human_ids import humanize


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
                response_check = req_with_auth(email=user.email) \
                    .get(API_URL + '/venueProviders/' + venue_provider_id)
                assert response_check.status_code == 200
                read_json = response_check.json()
                tries += 1
                sleep(2)
