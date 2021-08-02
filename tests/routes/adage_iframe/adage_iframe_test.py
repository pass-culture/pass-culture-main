import datetime

import jwt

from pcapi.core.users.models import ALGORITHM_RS_256
from pcapi.routes.adage_iframe import blueprint
from pcapi.routes.adage_iframe.security import adage_jwt_required

from tests.conftest import TestClient
from tests.routes.adage_iframe import INVALID_RSA_PRIVATE_KEY_PATH
from tests.routes.adage_iframe import VALID_RSA_PRIVATE_KEY_PATH


@blueprint.adage_iframe.route("/", methods=["GET"])
@adage_jwt_required
def get_home_test(user_email: str = None) -> str:
    return {"user_email": user_email}


class Returns200Test:
    def test_should_return_success_response_when_jwt_valid(self, app):
        # Given
        now = datetime.datetime.utcnow()
        test_client = TestClient(app.test_client())
        with open(VALID_RSA_PRIVATE_KEY_PATH, "rb") as reader:
            valid_encoded_token = jwt.encode(
                {"email": "jean@test.com", "exp": now + datetime.timedelta(days=1)},
                key=reader.read(),
                algorithm=ALGORITHM_RS_256,
            )

        test_client.auth_header = {"Authorization": f"Bearer {valid_encoded_token}"}

        # When
        response = test_client.get("/adage-iframe/")

        # Then
        assert response.status_code == 200
        assert response.json["user_email"] == "jean@test.com"


class ReturnsErrorTest:
    def test_should_return_error_response_when_jwt_invalid(self, app):
        # Given
        now = datetime.datetime.utcnow()
        test_client = TestClient(app.test_client())
        with open(INVALID_RSA_PRIVATE_KEY_PATH, "rb") as reader:
            corrupted_token = jwt.encode(
                {"email": "jean@test.com", "exp": now + datetime.timedelta(days=1)},
                key=reader.read(),
                algorithm=ALGORITHM_RS_256,
            )

        test_client.auth_header = {"Authorization": f"Bearer {corrupted_token}"}

        # When
        response = test_client.get("/adage-iframe/")

        # Then
        assert response.status_code == 403
        assert "Unrecognized token" in response.json["Authorization"]

    def test_should_return_error_response_when_jwt_expired(self, app):
        # Given
        now = datetime.datetime.utcnow()
        test_client = TestClient(app.test_client())
        with open(VALID_RSA_PRIVATE_KEY_PATH, "rb") as reader:
            expired_token = jwt.encode(
                {"email": "jean@test.com", "exp": now - datetime.timedelta(days=1)},
                key=reader.read(),
                algorithm=ALGORITHM_RS_256,
            )

        test_client.auth_header = {"Authorization": f"Bearer {expired_token}"}

        # When
        response = test_client.get("/adage-iframe/")

        # Then
        assert response.status_code == 422
        assert "Token expired" in response.json["msg"]

    def test_should_return_error_response_when_no_expiration_date_in_token(self, app):
        # Given
        test_client = TestClient(app.test_client())
        with open(VALID_RSA_PRIVATE_KEY_PATH, "rb") as reader:
            no_expiration_date_token = jwt.encode(
                {"email": "jean@test.com"},
                key=reader.read(),
                algorithm=ALGORITHM_RS_256,
            )

        test_client.auth_header = {"Authorization": f"Bearer {no_expiration_date_token}"}

        # When
        response = test_client.get("/adage-iframe/")

        # Then
        assert response.status_code == 422
        assert "No expiration date provided" in response.json["msg"]
