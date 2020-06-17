from tests.conftest import clean_database, TestClient
from unittest.mock import call, patch
from workers.bank_information_job import bank_information_job


class Post:
    class Returns200:
        def when_has_the_exact_payload(self, app):
            # Given
            data = {'token': 'authorized-token'}

            # When
            response = TestClient(app.test_client()) \
                .post('/beneficiaries/licence_verify', json=data)

            # Then
            assert response.status_code == 200

    class Returns422:
        def when_token_is_wrong(self, app):
            # Given
            data = {'token': 'wrong-token'}

            # When
            response = TestClient(app.test_client()) \
                .post(f'/beneficiaries/licence_verify', json=data)

            # Then
            assert response.status_code == 422

    class Returns400:
        def when_has_no_payload(self, app):
            # When
            response = TestClient(app.test_client()) \
                .post('/beneficiaries/licence_verify')

            # Then
            assert response.status_code == 400

        def when_has_wrong_token_key(self, app):
            # Given
            data = {'custom-token': 'authorized-token'}

            # When
            response = TestClient(app.test_client()) \
                .post('/beneficiaries/licence_verify', json=data)

            # Then
            assert response.status_code == 400
