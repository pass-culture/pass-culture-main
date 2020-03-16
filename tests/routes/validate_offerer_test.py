import secrets
from unittest.mock import patch

from models import Offerer
from repository import repository
from tests.conftest import clean_database, TestClient
from tests.model_creators.generic_creators import create_user, create_offerer, create_user_offerer, create_venue


class Get:
    class Returns202:
        @clean_database
        def expect_offerer_to_be_validated(self, app):
            # Given
            offerer_token = secrets.token_urlsafe(20)
            offerer = create_offerer(siren='349974931', address='12 boulevard de Pesaro', city='Nanterre', postal_code='92000', name='Crédit Coopératif',
                                     validation_token=offerer_token)
            user = create_user()
            user_offerer = create_user_offerer(user, offerer, is_admin=True)
            repository.save(offerer, user_offerer)
            offerer_id = offerer.id
            del (offerer)

            token = Offerer.query \
                .filter_by(id=offerer_id) \
                .first().validationToken

            # When
            response = TestClient(app.test_client()).get(f'/validate/offerer/{token}',
                                                         headers={'origin': 'http://localhost:3000'})

            # Then
            assert response.status_code == 202
            offerer = Offerer.query \
                .filter_by(id=offerer_id) \
                .first()
            assert offerer.isValidated

        @patch('routes.validate.link_valid_venue_to_irises')
        @clean_database
        def expect_link_venue_to_iris_if_valid_to_have_been_called_for_every_venue(self, mocked_link_venue_to_iris_if_valid, app):
            # Given
            offerer_token = secrets.token_urlsafe(20)
            offerer = create_offerer(validation_token=offerer_token)
            venue_1 = create_venue(offerer)
            venue_2 = create_venue(offerer, siret=offerer.siren + '65371')
            venue_3 = create_venue(offerer, is_virtual=True, siret=None)
            user = create_user()
            user_offerer = create_user_offerer(user, offerer, is_admin=True)

            repository.save(venue_1, venue_2, venue_3, user_offerer)

            # When
            response = TestClient(app.test_client()).get(f'/validate/offerer/{offerer_token}',
                                                         headers={'origin': 'http://localhost:3000'})

            # Then
            assert response.status_code == 202
            assert mocked_link_venue_to_iris_if_valid.call_count == 3

    class Returns404:
        @clean_database
        def expect_offerer_not_to_be_validated_with_unknown_token(self, app):
            # when
            response = TestClient(app.test_client()).with_auth(email='toto_pro@btmx.fr') \
                .get('/validate/offerer/123')

            # then
            assert response.status_code == 404

