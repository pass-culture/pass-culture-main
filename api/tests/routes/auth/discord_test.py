import unittest

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from flask import g
from flask import url_for
import pytest

from pcapi import settings
from pcapi.core.history import factories as history_factories
from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import override_settings
from pcapi.core.users import constants as users_constants
from pcapi.core.users import factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


class DiscordSigninTest:
    endpoint = "auth.discord_signin"
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
    )
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    public_key = private_key.public_key()
    public_key_pem = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    def fetch_csrf_token(self, client):
        # will generate a csrf token
        client.get(url_for("auth.discord_signin"))

    def post_to_endpoint(
        self,
        client,
        form=None,
        headers=None,
        follow_redirects=False,
        expected_num_queries: int | None = None,
        **url_kwargs,
    ):
        self.fetch_csrf_token(client)
        url = url_for(self.endpoint, **url_kwargs)

        if form is None:
            form = {}
        form["csrf_token"] = g.get("csrf_token", None)
        if expected_num_queries is not None:
            with assert_num_queries(expected_num_queries):
                return client.post(url, form=form, headers=headers, follow_redirects=follow_redirects)

        return client.post(url, form=form, headers=headers, follow_redirects=follow_redirects)

    @override_settings(DISCORD_JWT_PUBLIC_KEY=public_key_pem, DISCORD_JWT_PRIVATE_KEY=private_key_pem)
    def test_successful_discord_signing(self, client, db_session):
        redirect_url = "https://test.com"
        form_data = {
            "email": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "discord_id": "1234",
            "redirect_url": redirect_url,
        }
        user = users_factories.UserFactory(email=form_data["email"], password=form_data["password"], isActive=True)
        discord_user = users_factories.DiscordUserFactory(user=user, discordId=None, hasAccess=True, isBanned=False)

        response = self.post_to_endpoint(client, form=form_data)

        assert response.status_code == 302
        assert response.location == redirect_url

        db_session.refresh(discord_user)
        assert discord_user.discordId == form_data["discord_id"]

    @unittest.mock.patch(
        "pcapi.routes.auth.discord.discord_connector.retrieve_access_token", return_value="discord_access_token"
    )
    @unittest.mock.patch("pcapi.routes.auth.discord.discord_connector.add_to_server")
    def test_discord_webhook(self, mock_add_to_server, mock_retrieve_access_token, client):
        client.get(url_for("auth.discord_call_back", code="discord_code"))

        assert mock_retrieve_access_token.call_count == 1
        assert mock_retrieve_access_token.call_args[0][0] == "discord_code"

        assert mock_add_to_server.call_count == 1
        assert mock_add_to_server.call_args[0][0] == "discord_access_token"

    @override_settings(DISCORD_JWT_PUBLIC_KEY=public_key_pem, DISCORD_JWT_PRIVATE_KEY=private_key_pem)
    def test_has_access_is_false(self, client, db_session):
        redirect_url = "https://test.com"
        form_data = {
            "email": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "discord_id": "1234",
            "redirect_url": redirect_url,
        }

        user = users_factories.UserFactory(email=form_data["email"], password=form_data["password"], isActive=True)
        discord_user = users_factories.DiscordUserFactory(user=user, discordId=None, hasAccess=False, isBanned=False)

        response = self.post_to_endpoint(client, form=form_data)

        assert response.status_code == 200
        assert response.location is None

        response_data = response.data.decode("utf-8")
        assert "Accès refusé au serveur Discord. Contacte le support pour plus d&#39;informations" in response_data

        db_session.refresh(discord_user)
        assert discord_user.discordId is None

    @override_settings(DISCORD_JWT_PUBLIC_KEY=public_key_pem, DISCORD_JWT_PRIVATE_KEY=private_key_pem)
    def test_discord_user_is_none(self, client):
        redirect_url = "https://test.com"
        form_data = {
            "email": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "discord_id": "1234",
            "redirect_url": redirect_url,
        }
        users_factories.UserFactory(email=form_data["email"], password=form_data["password"], isActive=True)

        response = self.post_to_endpoint(client, form=form_data)

        assert response.status_code == 200

        assert response.status_code == 200
        assert response.location is None

        response_data = response.data.decode("utf-8")
        assert "Accès refusé au serveur Discord. Contacte le support pour plus d&#39;informations" in response_data

    @override_settings(DISCORD_JWT_PUBLIC_KEY=public_key_pem, DISCORD_JWT_PRIVATE_KEY=private_key_pem)
    def test_discord_user_is_active(self, client):
        redirect_url = "https://test.com"
        form_data = {
            "email": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "discord_id": "1234",
            "redirect_url": redirect_url,
        }
        user = users_factories.UserFactory(email=form_data["email"], password=form_data["password"], isActive=True)
        users_factories.DiscordUserFactory(user=user, hasAccess=True, isBanned=False)

        response = self.post_to_endpoint(client, form=form_data)

        assert response.status_code == 302
        assert response.location == redirect_url

    def test_account_anonymized_user_request_account_state(self, client):
        form_data = {
            "email": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "discord_id": "1234",
            "redirect_url": "https://test.com",
        }
        users_factories.AnonymizedUserFactory(
            email=form_data["email"],
            password=form_data["password"],
        )
        response = self.post_to_endpoint(client, form=form_data)
        assert response.status_code == 200

        response_data = response.data.decode("utf-8")
        assert "Le compte a été anonymisé" in response_data

    def test_wrong_password(self, client):
        form_data = {
            "email": "user@test.com",
            "password": "wrong_password",
            "discord_id": "1234",
            "redirect_url": "https://test.com",
        }
        users_factories.AnonymizedUserFactory(
            email=form_data["email"],
            password=settings.TEST_DEFAULT_PASSWORD,
        )
        response = self.post_to_endpoint(client, form=form_data)
        assert response.status_code == 200

        response_data = response.data.decode("utf-8")
        assert "Identifiant ou Mot de passe incorrect" in response_data

    def test_account_deleted_account_state(self, client):
        form_data = {
            "email": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "discord_id": "1234",
            "redirect_url": "https://test.com",
        }
        user = users_factories.UserFactory(email=form_data["email"], password=form_data["password"], isActive=False)
        history_factories.SuspendedUserActionHistoryFactory(user=user, reason=users_constants.SuspensionReason.DELETED)

        response = self.post_to_endpoint(client, form=form_data)
        assert response.status_code == 200

        response_data = response.data.decode("utf-8")
        assert "Le compte a été supprimé" in response_data

    def test_inactive_user_signin(self, client):
        form_data = {
            "email": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "discord_id": "1234",
            "redirect_url": "https://test.com",
        }
        users_factories.BaseUserFactory(email=form_data["email"], password=form_data["password"])
        response = self.post_to_endpoint(client, form=form_data)
        assert response.status_code == 200

        response_data = response.data.decode("utf-8")
        assert (
            "L&#39;email n&#39;a pas été validé. Valide ton compte sur le pass Culture pour continuer" in response_data
        )

    def test_unknown_user_logs_in(self, client):
        form_data = {
            "email": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "discord_id": "1234",
            "redirect_url": "https://test.com",
        }
        response = self.post_to_endpoint(client, form=form_data)
        assert response.status_code == 200

        response_data = response.data.decode("utf-8")
        assert "Identifiant ou Mot de passe incorrect" in response_data

    def test_user_without_password_logs_in(self, client):
        user = users_factories.UserFactory(password=None, isActive=True)
        form_data = {
            "email": user.email,
            "password": settings.TEST_DEFAULT_PASSWORD,
            "discord_id": "1234",
            "redirect_url": "https://test.com",
        }
        response = self.post_to_endpoint(client, form=form_data)
        assert response.status_code == 200

        response_data = response.data.decode("utf-8")
        assert "Identifiant ou Mot de passe incorrect" in response_data

    def test_user_logs_in_with_missing_fields(self, client):
        form_data = {
            "email": "user@test.com",
            "discord_id": "1234",
            "redirect_url": "https://test.com",
        }
        response = self.post_to_endpoint(client, form=form_data)
        assert response.status_code == 200
