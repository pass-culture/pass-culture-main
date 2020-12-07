from unittest.mock import MagicMock
from unittest.mock import patch

from pcapi.validation.routes.captcha import InvalidRecaptchaTokenException

from tests.conftest import TestClient


token_is_valid_mock = MagicMock()
token_is_wrong_mock = MagicMock(side_effect=InvalidRecaptchaTokenException())


class Post:
    class Returns200:
        @patch("pcapi.core.users.repository.get_id_check_token", lambda x: None)
        @patch("pcapi.routes.webapp.beneficiaries.check_recaptcha_token_is_valid", token_is_valid_mock)
        def when_has_the_exact_payload(self, app):
            # Given
            data = {"token": "authorized-token"}

            # When
            response = TestClient(app.test_client()).post("/beneficiaries/licence_verify", json=data)

            # Then
            assert response.status_code == 200

        @patch("pcapi.core.users.repository.get_id_check_token", lambda x: "authorized-token")
        def when_has_an_existing_JWT_token(self, app):
            # Given
            data = {"token": "authorized-token"}

            # When
            response = TestClient(app.test_client()).post("/beneficiaries/licence_verify", json=data)

            # Then
            assert response.status_code == 200

    class Returns400:
        @patch("pcapi.routes.webapp.beneficiaries.check_recaptcha_token_is_valid", token_is_wrong_mock)
        def when_token_is_wrong(self, app):
            # Given
            data = {"token": "wrong-token"}

            # When
            response = TestClient(app.test_client()).post("/beneficiaries/licence_verify", json=data)

            # Then
            assert response.status_code == 400
            assert response.json["token"] == ["Le token renseigné n'est pas valide"]

        @patch("pcapi.routes.webapp.beneficiaries.check_recaptcha_token_is_valid", token_is_valid_mock)
        def when_has_no_payload(self, app):
            # When
            response = TestClient(app.test_client()).post("/beneficiaries/licence_verify")

            # Then
            assert response.status_code == 400

        @patch("pcapi.routes.webapp.beneficiaries.check_recaptcha_token_is_valid", token_is_valid_mock)
        def when_token_is_null(self, app):
            # Given
            data = {"token": None}

            # When
            response = TestClient(app.test_client()).post("/beneficiaries/licence_verify", json=data)

            # Then
            assert response.status_code == 400

        @patch("pcapi.routes.webapp.beneficiaries.check_recaptcha_token_is_valid", token_is_valid_mock)
        def when_token_is_the_string_null(self, app):
            # Given
            data = {"token": "null"}

            # When
            response = TestClient(app.test_client()).post("/beneficiaries/licence_verify", json=data)

            # Then
            assert response.status_code == 400

        @patch("pcapi.routes.webapp.beneficiaries.check_recaptcha_token_is_valid", token_is_valid_mock)
        def when_has_wrong_token_key(self, app):
            # Given
            data = {"custom-token": "authorized-token"}

            # When
            response = TestClient(app.test_client()).post("/beneficiaries/licence_verify", json=data)

            # Then
            assert response.status_code == 400
