import pytest
from tests.conftest import TestClient
from pcapi.core.users.factories import UserFactory


def test_send_reset_password_email_without_email(app):
    response = TestClient(app.test_client()).post("/native/v1/password_reset_request")

    assert response.status_code == 400
    assert response.json["email"] == ["Ce champ est obligatoire"]


def test_request_reset_password_for_unknown_email(app):
    data = {"email": "not_existing_user@email.com"}
    response = TestClient(app.test_client()).post("/native/v1/password_reset_request", json=data)

    assert response.status_code == 204


@pytest.mark.usefixtures("db_session")
def test_request_reset_password_for_existing_email(app):
    email = "existing_user@email.com"
    data = {"email": email}
    user = UserFactory(email=email)
    response = TestClient(app.test_client()).post("/native/v1/password_reset_request", json=data)

    assert response.status_code == 204
    assert user.resetPasswordToken is not None
