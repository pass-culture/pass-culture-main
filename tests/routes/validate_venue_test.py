from models.db import db
from repository import repository
from tests.conftest import clean_database, TestClient
from tests.model_creators.generic_creators import create_offerer, create_venue


class Get:
    class Returns202:
        @clean_database
        def expect_validation_token_to_be_none(self, app):
            # Given
            offerer = create_offerer()
            venue = create_venue(offerer)
            venue.generate_validation_token()
            repository.save(venue)

            token = venue.validationToken

            # When
            response = TestClient(app.test_client()).get('/validate/venue?token={}'.format(token))

            # Then
            assert response.status_code == 202
            db.session.refresh(venue)
            assert venue.isValidated

    class Returns400:
        @clean_database
        def when_no_validation_token_is_provided(self, app):
            # When
            response = TestClient(app.test_client()).get('/validate/venue')

            # Then
            assert response.status_code == 400
            assert response.json['token'] == ['Vous devez fournir un jeton de validation']

    class Returns404:
        @clean_database
        def when_validation_token_is_unknown(self, app):
            # When
            response = TestClient(app.test_client()).get('/validate/venue?token={}'.format('12345'))

            # Then
            assert response.status_code == 404
            assert response.json['token'] == ['Jeton inconnu']
