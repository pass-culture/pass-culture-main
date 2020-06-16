from tests.conftest import clean_database, TestClient
from unittest.mock import call, patch
from workers.bank_information_job import bank_information_job


class Post:
    class Returns200:
        def when_has_the_good_token(self, app):
            # Given
            token = "authorized-token"

            # When
            response = TestClient(app.test_client()) \
                .post(f'/beneficiaries/licence_verify?token={token}')

            # Then
            assert response.status_code == 200

    class Returns422:
        def when_has_not_the_good_token(self, app):
            # Given
            token = "wrong-token"

            # When
            response = TestClient(app.test_client()) \
                .post(f'/beneficiaries/licence_verify?token={token}')

            # Then
            assert response.status_code == 422

        def when_has_not_any_token(self, app):
            # When
            response = TestClient(app.test_client()) \
                .post('/beneficiaries/licence_verify')

            # Then
            assert response.status_code == 422
