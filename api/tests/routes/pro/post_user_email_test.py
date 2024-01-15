from typing import Any
from unittest.mock import patch
from urllib.parse import parse_qs
from urllib.parse import urlparse

import pytest

from pcapi import settings
import pcapi.core.mails.testing as mails_testing
from pcapi.core.users import factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


class ProUpdateEmailTest:
    origin_email = "email@example.com"
    new_email = "updated_" + origin_email

    def test_beneficiary_updates_pro_email_(self, client: Any) -> None:
        user = users_factories.BeneficiaryGrant18Factory(email=self.origin_email)
        form_data = {"email": self.new_email, "password": settings.TEST_DEFAULT_PASSWORD}
        client = client.with_session_auth(user.email)
        response = client.post("/users/email", json=form_data)

        assert response.status_code == 400
        assert user.email == self.origin_email

    def test_update_pro_email(self, client: Any) -> None:
        pro = users_factories.ProFactory(email=self.origin_email)
        form_data = {"email": self.new_email, "password": settings.TEST_DEFAULT_PASSWORD}
        client = client.with_session_auth(pro.email)
        response = client.post("/users/email", json=form_data)

        assert response.status_code == 204
        assert pro.email == self.origin_email
        assert mails_testing.outbox[0]["To"] == self.origin_email
        assert mails_testing.outbox[0]["params"] == {
            "NEW_EMAIL": self.new_email,
            "OLD_EMAIL": self.origin_email,
        }
        assert mails_testing.outbox[-1]["To"] == self.new_email
        assert len(mails_testing.outbox) == 2

        activation_email = mails_testing.outbox[-1]
        confirmation_link = urlparse(activation_email["params"]["CONFIRMATION_LINK"])
        base_url_params = parse_qs(confirmation_link.query)
        assert {"token"} == base_url_params.keys()

    def test_update_email_missing_password(self, client):
        pro = users_factories.ProFactory(email=self.origin_email)
        form_data = {"email": self.new_email}

        client = client.with_session_auth(pro.email)
        response = client.post("/users/email", json=form_data)

        assert response.status_code == 400
        assert "password" in response.json

        assert pro.email == self.origin_email
        assert not mails_testing.outbox

    @pytest.mark.parametrize(
        "email,password",
        [
            ("new@example.com", "not_the_users_password"),
            ("invalid.password@format.com", "short"),
            ("not_an_email", "some_random_string"),
        ],
    )
    def test_update_email_errors(self, client, app, email, password):
        pro = users_factories.UserFactory(email=self.origin_email)
        client = client.with_session_auth(pro.email)
        form_data = {"email": email, "password": password}
        response = client.post("/users/email", json=form_data)

        assert response.status_code == 400
        assert pro.email == self.origin_email
        assert not mails_testing.outbox

    def test_update_email_existing_email(self, app, client):
        """
        Test that if the email already exists, an OK response is sent
        but nothing is sent (avoid user enumeration).
        """
        pro = users_factories.ProFactory(email=self.origin_email)
        other_user = users_factories.ProFactory(email="other_" + self.origin_email)

        client = client.with_session_auth(pro.email)
        response = client.post(
            "/users/email",
            json={
                "email": other_user.email,
                "password": settings.TEST_DEFAULT_PASSWORD,
            },
        )
        assert response.status_code == 400
        assert response.json == {"email": ["Un compte lié à cet email existe déjà"]}
        assert pro.email == self.origin_email
        assert not mails_testing.outbox

    @patch("pcapi.core.users.constants.MAX_EMAIL_UPDATE_ATTEMPTS_FOR_PRO", 1)
    def test_update_email_too_many_attempts(self, app, client):
        """
        Test that a user cannot request more than
        MAX_EMAIL_UPDATE_ATTEMPTS email update change within the last
        N days.
        """
        self.send_two_requests(client, "Trop de tentatives, réessayez dans 24 heures")

    def send_two_requests(self, client, error_message):
        pro = users_factories.ProFactory(email=self.origin_email)

        client = client.with_session_auth(pro.email)
        response = client.post(
            "/users/email",
            json={
                "email": "updated_" + pro.email,
                "password": settings.TEST_DEFAULT_PASSWORD,
            },
        )

        assert response.status_code == 204

        client = client.with_session_auth(pro.email)
        response = client.post(
            "/users/email",
            json={
                "email": "updated_twice_" + pro.email,
                "password": settings.TEST_DEFAULT_PASSWORD,
            },
        )

        assert response.status_code == 400
        assert response.json == {"email": [error_message]}
