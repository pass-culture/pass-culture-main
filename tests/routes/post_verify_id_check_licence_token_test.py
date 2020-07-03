from unittest.mock import patch
from tests.conftest import TestClient


def check_token_mock(token: str):
    return token == 'authorized-token'

class Post:
    class Returns200:
        @patch("routes.beneficiaries.check_licence_token_is_valid", check_token_mock)
        def when_has_the_exact_payload(self, app):
            # Given
            data = {'token': 'authorized-token'}

            # When
            response = TestClient(app.test_client()) \
                .post('/beneficiaries/licence_verify', json=data)

            # Then
            assert response.status_code == 200

    class Returns422:
        @patch("routes.beneficiaries.check_licence_token_is_valid", check_token_mock)
        def when_token_is_wrong(self, app):
            # Given
            data = {'token': 'wrong-token'}

            # When
            response = TestClient(app.test_client()) \
                .post(f'/beneficiaries/licence_verify', json=data)

            # Then
            assert response.status_code == 422

    class Returns400:
        @patch("routes.beneficiaries.check_licence_token_is_valid", check_token_mock)
        def when_has_no_payload(self, app):
            # When
            response = TestClient(app.test_client()) \
                .post('/beneficiaries/licence_verify')

            # Then
            assert response.status_code == 400

        @patch("routes.beneficiaries.check_licence_token_is_valid", check_token_mock)
        def when_has_wrong_token_key(self, app):
            # Given
            data = {'custom-token': 'authorized-token'}

            # When
            response = TestClient(app.test_client()) \
                .post('/beneficiaries/licence_verify', json=data)

            # Then
            assert response.status_code == 400
