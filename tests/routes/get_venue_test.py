from models import PcObject
from tests.conftest import clean_database, TestClient
from tests.test_utils import API_URL, create_venue, create_offerer, create_user, create_user_offerer, \
    create_bank_information
from utils.human_ids import humanize


class Get:
    class Returns200:
        @clean_database
        def when_user_has_rights_on_managing_offerer(self, app):
            # given
            offerer = create_offerer()
            user = create_user(email='user.pro@test.com')
            user_offerer = create_user_offerer(user, offerer)
            venue = create_venue(offerer, name='L\'encre et la plume')
            bank_information = create_bank_information(bic='QSDFGH8Z555', iban='FR7630006000011234567890189',
                                                       venue=venue)
            PcObject.save(user_offerer, bank_information)
            auth_request = TestClient().with_auth(email=user.email)

            # when
            response = auth_request.get(API_URL + '/venues/%s' % humanize(venue.id))

            # then
            assert response.status_code == 200
            response_json = response.json()
            assert response_json['bic'] == 'QSDFGH8Z555'
            assert response_json['iban'] == 'FR7630006000011234567890189'
            assert 'validationToken' not in response_json

    class Returns403:
        @clean_database
        def when_current_user_doesnt_have_rights(self, app):
            # given
            offerer = create_offerer()
            user = create_user(email='user.pro@test.com')
            venue = create_venue(offerer, name='L\'encre et la plume')
            PcObject.save(user, venue)
            auth_request = TestClient().with_auth(email=user.email)

            # when
            response = auth_request.get(API_URL + '/venues/%s' % humanize(venue.id))

            # then
            assert response.status_code == 403
            assert response.json()['global'] == ["Cette structure n'est pas enregistrée chez cet utilisateur."]
