import secrets

from models import Offerer, PcObject
from tests.conftest import clean_database, TestClient
from tests.model_creators.generic_creators import create_user, create_offerer, create_user_offerer


class Get:
    class Returns202:
        @clean_database
        def expect_offerer_to_be_validated(self, app):
            # Given
            offerer_token = secrets.token_urlsafe(20)
            offerer = create_offerer('349974931', '12 boulevard de Pesaro', 'Nanterre', '92000', 'Crédit Coopératif',
                                     validation_token=offerer_token)
            user = create_user()
            user_offerer = create_user_offerer(user, offerer, is_admin=True)
            PcObject.save(offerer, user_offerer)
            offerer_id = offerer.id
            del (offerer)

            token = Offerer.query \
                .filter_by(id=offerer_id) \
                .first().validationToken

            # When
            response = TestClient(app.test_client()).get('/validate?modelNames=Offerer&token=' + token,
                                                         headers={'origin': 'http://localhost:3000'})

            # Then
            assert response.status_code == 202
            offerer = Offerer.query \
                .filter_by(id=offerer_id) \
                .first()
            assert offerer.isValidated

    class Returns404:
        @clean_database
        def expect_offerer_not_to_be_validated_with_unknown_token(self, app):
            # when
            response = TestClient(app.test_client()).with_auth(email='toto_pro@btmx.fr') \
                .get('/validate?modelNames=Offerer&token=123')

            # then
            assert response.status_code == 404
