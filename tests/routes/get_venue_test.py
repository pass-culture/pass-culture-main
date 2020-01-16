from repository.repository import Repository
from tests.conftest import clean_database, TestClient
from tests.model_creators.generic_creators import create_user, create_offerer, create_venue, create_user_offerer, \
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
            Repository.save(user_offerer, bank_information)
            auth_request = TestClient(app.test_client()).with_auth(email=user.email)

            # when
            response = auth_request.get('/venues/%s' % humanize(venue.id))

            # then
            assert response.status_code == 200
            response_json = response.json
            assert response_json['bic'] == 'QSDFGH8Z555'
            assert response_json['iban'] == 'FR7630006000011234567890189'
            assert 'validationToken' not in response_json
            assert 'validationToken' not in response_json['managingOfferer']

    class Returns403:
        @clean_database
        def when_current_user_doesnt_have_rights(self, app):
            # given
            offerer = create_offerer()
            user = create_user(email='user.pro@test.com')
            venue = create_venue(offerer, name='L\'encre et la plume')
            Repository.save(user, venue)
            auth_request = TestClient(app.test_client()).with_auth(email=user.email)

            # when
            response = auth_request.get('/venues/%s' % humanize(venue.id))

            # then
            assert response.status_code == 403
            assert response.json['global'] == [
                "Vous n'avez pas les droits d'accès suffisant pour accéder à cette information."]
