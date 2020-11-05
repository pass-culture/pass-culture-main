from unittest.mock import patch

import pytest

from pcapi.core.users.factories import UserFactory
from pcapi.models.api_errors import ApiErrors
from pcapi.utils.mailing import MailServiceException
from tests.conftest import TestClient

pytestmark = pytest.mark.usefixtures("db_session")

def test_send_reset_password_email_without_email(app):
    response = TestClient(app.test_client()).post("/native/v1/password_reset_request")

    assert response.status_code == 400
    assert response.json["email"] == ["Ce champ est obligatoire"]


def test_request_reset_password_for_unknown_email(app):
    data = {"email": "not_existing_user@example.com"}
    response = TestClient(app.test_client()).post("/native/v1/password_reset_request", json=data)

    assert response.status_code == 204


def test_request_reset_password_for_existing_email(app):
    email = "existing_user@example.com"
    data = {"email": email}
    user = UserFactory(email=email)
    response = TestClient(app.test_client()).post("/native/v1/password_reset_request", json=data)

    assert response.status_code == 204
    assert user.resetPasswordToken is not None

@pytest.mark.usefixtures("db_session")
@patch('pcapi.routes.native.v1.authentication.send_reset_password_email_to_user')
def test_request_reset_password_with_mail_service_exception(mock_send_reset_password_email_to_user, app):
    email = "existing_user@example.com"
    data = {"email": email}
    UserFactory(email=email)

    mock_send_reset_password_email_to_user.side_effect = MailServiceException()

    response = TestClient(app.test_client()).post("/native/v1/password_reset_request", json=data)

    assert response.status_code == 500
