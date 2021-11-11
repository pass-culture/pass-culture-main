from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from pcapi.connectors.api_recaptcha import InvalidRecaptchaTokenException
from pcapi.connectors.api_recaptcha import ReCaptchaException
from pcapi.core.users.factories import IdCheckToken
from pcapi.core.users.factories import UserFactory

from tests.conftest import TestClient


token_is_valid_mock = MagicMock()
token_is_wrong_mock = MagicMock(side_effect=InvalidRecaptchaTokenException())
token_is_totaly_weird_mock = MagicMock(side_effect=ReCaptchaException())


@pytest.mark.usefixtures("db_session")
class Returns200Test:
    @patch("pcapi.core.users.repository.get_id_check_token", lambda x: None)
    @patch("pcapi.routes.webapp.beneficiaries.check_webapp_recaptcha_token", token_is_valid_mock)
    def when_has_the_exact_payload(self, app):
        # Given
        data = {"token": "authorized-token"}

        # When
        response = TestClient(app.test_client()).post("/beneficiaries/licence_verify", json=data)

        # Then
        assert response.status_code == 200

    def when_has_an_existing_JWT_token(self, app):
        # Given
        user = UserFactory()
        IdCheckToken(user=user, isUsed=False, value="authorized-token")

        data = {"token": "authorized-token"}

        # When
        response = TestClient(app.test_client()).post("/beneficiaries/licence_verify", json=data)

        # Then
        assert response.status_code == 200


@pytest.mark.usefixtures("db_session")
class Returns400Test:
    @patch("pcapi.routes.webapp.beneficiaries.check_webapp_recaptcha_token", token_is_wrong_mock)
    def when_token_is_wrong(self, app):
        # Given
        data = {"token": "wrong-token"}

        # When
        response = TestClient(app.test_client()).post("/beneficiaries/licence_verify", json=data)

        # Then
        assert response.status_code == 400
        assert response.json["token"] == ["Le token renseigné n'est pas valide"]

    @patch("pcapi.routes.webapp.beneficiaries.check_webapp_recaptcha_token", token_is_totaly_weird_mock)
    def when_has_an_expired_JWT_token(self, app):
        # Given
        user = UserFactory()
        IdCheckToken(user=user, isUsed=True, value="authorized-token")

        data = {"token": "authorized-token"}

        # When
        response = TestClient(app.test_client()).post("/beneficiaries/licence_verify", json=data)

        # Then
        assert response.status_code == 400
        assert response.json["token"] == "Le token renseigné n'est pas valide"

    @patch("pcapi.routes.webapp.beneficiaries.check_webapp_recaptcha_token", token_is_valid_mock)
    def when_has_no_payload(self, app):
        # When
        response = TestClient(app.test_client()).post("/beneficiaries/licence_verify")

        # Then
        assert response.status_code == 400

    @patch("pcapi.routes.webapp.beneficiaries.check_webapp_recaptcha_token", token_is_valid_mock)
    def when_token_is_null(self, app):
        # Given
        data = {"token": None}

        # When
        response = TestClient(app.test_client()).post("/beneficiaries/licence_verify", json=data)

        # Then
        assert response.status_code == 400

    @patch("pcapi.routes.webapp.beneficiaries.check_webapp_recaptcha_token", token_is_valid_mock)
    def when_token_is_the_string_null(self, app):
        # Given
        data = {"token": "null"}

        # When
        response = TestClient(app.test_client()).post("/beneficiaries/licence_verify", json=data)

        # Then
        assert response.status_code == 400

    @patch("pcapi.routes.webapp.beneficiaries.check_webapp_recaptcha_token", token_is_valid_mock)
    def when_has_wrong_token_key(self, app):
        # Given
        data = {"custom-token": "authorized-token"}

        # When
        response = TestClient(app.test_client()).post("/beneficiaries/licence_verify", json=data)

        # Then
        assert response.status_code == 400
