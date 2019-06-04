import pytest

from models import PcObject
from tests.conftest import clean_database, TestClient
from tests.test_utils import API_URL, \
    create_user, create_offerer, create_venue, create_bank_information, create_user_offerer
from utils.human_ids import humanize


class Get:
    class Returns404:
        @clean_database
        def when_user_offerer_does_not_exist(self, app):
            # Given
            user = create_user()
            PcObject.save(user)
            invalid_id = 12

            # When
            response = TestClient() \
                .with_auth(user.email) \
                .get(API_URL + '/offerers/%s' % invalid_id)

            # then
            assert response.status_code == 404
            assert response.json()['global'] == ['La page que vous recherchez n\'existe pas']

    class Returns200:
        @clean_database
        def when_user_has_rights_on_offerer(self, app):
            # given
            user = create_user()
            offerer = create_offerer()
            venue = create_venue(offerer)
            create_bank_information(venue=venue, id_at_providers=venue.siret)
            user_offerer = create_user_offerer(user, offerer)
            PcObject.save(user_offerer, venue)
            # when
            response = TestClient() \
                .with_auth(user.email) \
                .get(API_URL + f'/offerers/{humanize(offerer.id)}')

            # then
            assert response.status_code == 200
            response_json = response.json()
            assert 'bic' in response_json['managedVenues'][0]
            assert 'iban' in response_json['managedVenues'][0]
