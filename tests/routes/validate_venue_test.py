from models import PcObject
from models.db import db
from tests.conftest import clean_database, TestClient
from tests.test_utils import API_URL, create_offerer, create_venue


class Get:
    class Returns202:
        @clean_database
        def expect_validation_token_to_be_none(self, app):
            # Given
            offerer = create_offerer()
            venue = create_venue(offerer)
            venue.generate_validation_token()
            PcObject.save(venue)

            token = venue.validationToken

            # When
            response = TestClient().get('{}/validate/venue?token={}'.format(API_URL, token),
                                        headers={'origin': 'http://localhost:3000'})

            # Then
            assert response.status_code == 202
            db.session.refresh(venue)
            assert venue.isValidated

    class Returns400:
        @clean_database
        def when_no_validation_token_is_provided(self, app):
            # When
            response = TestClient().get('{}/validate/venue'.format(API_URL),
                                        headers={'origin': 'http://localhost:3000'})

            # Then
            assert response.status_code == 400
            assert response.json()['token'] == ['Vous devez fournir un jeton de validation']

    class Returns404:
        @clean_database
        def when_validation_token_is_unknown(self, app):
            # When
            response = TestClient().get('{}/validate/venue?token={}'.format(API_URL, '12345'),
                                        headers={'origin': 'http://localhost:3000'})

            # Then
            assert response.status_code == 404
            assert response.json()['token'] == ['Jeton inconnu']
