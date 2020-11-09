import typing
from unittest.mock import patch

from pcapi.connectors.api_recaptcha import ReCaptchaException

from tests.conftest import TestClient


def check_token_mock(token: str):
    return token == 'authorized-token'


def check_token_failed_mock(token: typing.Optional[str]):
    raise ReCaptchaException("Encountered the following error(s): whatever")


class Post:
    class Returns200:
        @patch("pcapi.routes.beneficiaries.is_licence_token_valid", check_token_mock)
        def when_has_the_exact_payload(self, app):
            # Given
            data = {'token': 'authorized-token'}

            # When
            response = TestClient(app.test_client()) \
                .post('/beneficiaries/licence_verify', json=data)

            # Then
            assert response.status_code == 200

    class Returns422:
        @patch("pcapi.routes.beneficiaries.is_licence_token_valid", check_token_mock)
        def when_token_is_wrong(self, app):
            # Given
            data = {'token': 'wrong-token'}

            # When
            response = TestClient(app.test_client()) \
                .post(f'/beneficiaries/licence_verify', json=data)

            # Then
            assert response.status_code == 422


    class Returns400:
        @patch("pcapi.routes.beneficiaries.is_licence_token_valid", check_token_mock)
        def when_has_no_payload(self, app):
            # When
            response = TestClient(app.test_client()) \
                .post('/beneficiaries/licence_verify')

            # Then
            assert response.status_code == 400

        @patch("pcapi.routes.beneficiaries.is_licence_token_valid", check_token_failed_mock)
        def when_token_is_null(self, app):
            # Given
            data = {'token': None}

            # When
            response = TestClient(app.test_client()) \
                .post(f'/beneficiaries/licence_verify', json=data)

            # Then
            assert response.status_code == 400

        @patch("pcapi.routes.beneficiaries.is_licence_token_valid", check_token_failed_mock)
        def when_token_is_the_string_null(self, app):
            # Given
            data = {'token': "null"}

            # When
            response = TestClient(app.test_client()) \
                .post(f'/beneficiaries/licence_verify', json=data)

            # Then
            assert response.status_code == 400

        @patch("pcapi.routes.beneficiaries.is_licence_token_valid", check_token_mock)
        def when_has_wrong_token_key(self, app):
            # Given
            data = {'custom-token': 'authorized-token'}

            # When
            response = TestClient(app.test_client()) \
                .post('/beneficiaries/licence_verify', json=data)

            # Then
            assert response.status_code == 400
