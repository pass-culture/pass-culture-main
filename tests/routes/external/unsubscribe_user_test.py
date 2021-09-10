import pytest

from pcapi.core.testing import override_settings
from pcapi.core.users.factories import UserFactory
from pcapi.flask_app import db

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
class UnsubscribeUserTest:
    def test_unsubscribe_user(self, app):
        # Given
        existing_user = UserFactory(email="lucy.ellingson@kennet.ca")
        headers = {"origin": "http://localhost:3000", "X-Forwarded-For": "185.107.232.1"}
        data = {"email": "lucy.ellingson@kennet.ca"}
        assert existing_user.notificationSubscriptions["marketing_email"]

        # When
        response = TestClient(app.test_client()).post("/webhooks/sendinblue/unsubscribe", json=data, headers=headers)

        # Then
        assert response.status_code == 204
        db.session.refresh(existing_user)
        assert not existing_user.notificationSubscriptions["marketing_email"]

    def test_unsubscribe_user_from_forbidden_ip(self, app):
        # Given
        existing_user = UserFactory(email="lucy.ellingson@kennet.ca")
        assert existing_user.notificationSubscriptions["marketing_email"]

        headers = {"origin": "http://localhost:3000", "X-Forwarded-For": "127.0.0.1"}
        data = {"email": "lucy.ellingson@kennet.ca"}

        # When
        with override_settings(IS_DEV=False):
            response = TestClient(app.test_client()).post(
                "/webhooks/sendinblue/unsubscribe", json=data, headers=headers
            )

        # Then
        assert response.status_code == 401
        db.session.refresh(existing_user)
        assert existing_user.notificationSubscriptions["marketing_email"]

    def test_unsubscribe_user_bad_request(self, app):
        # Given
        existing_user = UserFactory(email="lucy.ellingson@kennet.ca")
        assert existing_user.notificationSubscriptions["marketing_email"]

        headers = {"origin": "http://localhost:3000", "X-Forwarded-For": "185.107.232.1"}
        data = {}

        # When
        response = TestClient(app.test_client()).post("/webhooks/sendinblue/unsubscribe", json=data, headers=headers)

        # Then
        assert response.status_code == 400
        db.session.refresh(existing_user)
        assert existing_user.notificationSubscriptions["marketing_email"]

    def test_unsubscribe_user_does_not_exist(self, app):
        # Given
        headers = {"origin": "http://localhost:3000", "X-Forwarded-For": "185.107.232.1"}
        data = {"email": "lucy.ellingson@kennet.ca"}

        # When
        response = TestClient(app.test_client()).post("/webhooks/sendinblue/unsubscribe", json=data, headers=headers)

        # Then
        assert response.status_code == 400
