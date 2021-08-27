import datetime
from typing import ByteString
from typing import Optional

from tests.conftest import TestClient
from tests.routes.adage_iframe.utils_create_test_token import create_adage_jwt_fake_invalid_token
from tests.routes.adage_iframe.utils_create_test_token import create_adage_jwt_fake_valid_token


class Returns204Test:
    valid_user = {
        "civilite": "Mme.",
        "nom": "LAPROF",
        "prenom": "Sabine",
        "mail": "sabine.laprof@example.com",
        "uai": "EAU123",
    }

    def _create_adage_valid_token(self) -> ByteString:
        return create_adage_jwt_fake_valid_token(
            civility=self.valid_user.get("civilite"),
            lastname=self.valid_user.get("nom"),
            firstname=self.valid_user.get("prenom"),
            email=self.valid_user.get("mail"),
            uai=self.valid_user.get("uai"),
        )

    def test_should_return_success_response_when_jwt_valid(self, app):
        # Given
        valid_encoded_token = self._create_adage_valid_token()

        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {valid_encoded_token}"}

        # When
        response = test_client.get("/adage-iframe/authenticate")

        # Then
        assert response.status_code == 204
        assert response.json is None


class ReturnsErrorTest:
    valid_user = {
        "civilite": "Mme.",
        "nom": "LAPROF",
        "prenom": "Sabine",
        "mail": "sabine.laprof@example.com",
        "uai": "EAU123",
    }

    def _create_adage_valid_token_from_expiration_date(
        self, expiration_date: Optional[datetime.datetime]
    ) -> ByteString:
        return create_adage_jwt_fake_valid_token(
            civility=self.valid_user.get("civilite"),
            lastname=self.valid_user.get("nom"),
            firstname=self.valid_user.get("prenom"),
            email=self.valid_user.get("mail"),
            uai=self.valid_user.get("uai"),
            expiration_date=expiration_date,
        )

    def _create_adage_invalid_token(self) -> ByteString:
        return create_adage_jwt_fake_invalid_token(
            civility="M.", lastname="TESTABLE", firstname="Pascal", email="pascal.testable@example.com", uai="321UAE"
        )

    def test_should_return_error_response_when_jwt_invalid(self, app):
        # Given
        corrupted_token = self._create_adage_invalid_token()

        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {corrupted_token}"}

        # When
        response = test_client.get("/adage-iframe/authenticate")

        # Then
        assert response.status_code == 403
        assert "Unrecognized token" in response.json["Authorization"]

    def test_should_return_error_response_when_jwt_expired(self, app):
        # Given
        now = datetime.datetime.utcnow()
        expired_token = self._create_adage_valid_token_from_expiration_date(
            expiration_date=now - datetime.timedelta(days=1)
        )

        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {expired_token}"}

        # When
        response = test_client.get("/adage-iframe/authenticate")

        # Then
        assert response.status_code == 422
        assert "Token expired" in response.json["msg"]

    def test_should_return_error_response_when_no_expiration_date_in_token(self, app):
        # Given
        no_expiration_date_token = self._create_adage_valid_token_from_expiration_date(expiration_date=None)

        test_client = TestClient(app.test_client())
        test_client.auth_header = {"Authorization": f"Bearer {no_expiration_date_token}"}

        # When
        response = test_client.get("/adage-iframe/authenticate")

        # Then
        assert response.status_code == 422
        assert "No expiration date provided" in response.json["msg"]
