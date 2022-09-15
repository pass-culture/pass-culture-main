import logging

import pytest

from pcapi.core.testing import override_settings
from pcapi.core.users.factories import UserFactory
from pcapi.models import db

from tests.conftest import TestClient


@pytest.mark.usefixtures("db_session")
class UnsubscribeUserTest:
    def test_unsubscribe_user(self, app):
        # Given
        existing_user = UserFactory(email="lucy.ellingson@kennet.ca")
        headers = {"X-Forwarded-For": "185.107.232.1"}
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

        headers = {"X-Forwarded-For": "127.0.0.1"}
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

        headers = {"X-Forwarded-For": "185.107.232.1"}
        data = {}

        # When
        response = TestClient(app.test_client()).post("/webhooks/sendinblue/unsubscribe", json=data, headers=headers)

        # Then
        assert response.status_code == 400
        db.session.refresh(existing_user)
        assert existing_user.notificationSubscriptions["marketing_email"]

    def test_unsubscribe_user_does_not_exist(self, app):
        # Given
        headers = {"X-Forwarded-For": "185.107.232.1"}
        data = {"email": "lucy.ellingson@kennet.ca"}

        # When
        response = TestClient(app.test_client()).post("/webhooks/sendinblue/unsubscribe", json=data, headers=headers)

        # Then
        assert response.status_code == 400


@pytest.mark.usefixtures("db_session")
class NotifyImportContactsTest:
    def test_notify_importcontacts(self, app, caplog):
        # Given
        headers = {"X-Forwarded-For": "1.179.112.9"}

        # When
        with caplog.at_level(logging.INFO):
            response = TestClient(app.test_client()).post("/webhooks/sendinblue/importcontacts/18/1", headers=headers)

        # Then
        assert response.status_code == 204
        assert caplog.records[0].message == "ContactsApi->import_contacts finished"
        assert caplog.records[0].extra == {
            "list_id": 18,
            "iteration": 1,
        }
