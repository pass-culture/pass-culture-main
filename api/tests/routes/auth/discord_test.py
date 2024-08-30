import unittest

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from flask import g
from flask import url_for
import pytest

from pcapi import settings
from pcapi.connectors import discord as discord_connector
from pcapi.core.history import factories as history_factories
from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import override_settings
from pcapi.core.users import constants as users_constants
from pcapi.core.users import factories as users_factories
from pcapi.utils import requests


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

    def test_build_discord_redirection_uri(self):
        assert (
            discord_connector.build_discord_redirection_uri("1")
            == f"https://discord.com/api/oauth2/authorize?client_id={discord_connector.DISCORD_CLIENT_ID}&redirect_uri={discord_connector.DISCORD_CALLBACK_URI}&response_type=code&scope=identify%20guilds.join&state=1"
        )

    @override_settings(DISCORD_JWT_PUBLIC_KEY=public_key_pem, DISCORD_JWT_PRIVATE_KEY=private_key_pem)
    def test_redirect_to_discord_on_post(self, client):
        form_data = {
            "email": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
        }
        user = users_factories.BeneficiaryFactory(
            email=form_data["email"], password=form_data["password"], isActive=True
        )

        response = self.post_to_endpoint(client, form=form_data)

        assert response.status_code == 302
        assert response.location == discord_connector.build_discord_redirection_uri(user.id)

    @unittest.mock.patch(
        "pcapi.routes.auth.discord.discord_connector.retrieve_access_token", return_value="access_token"
    )
    @unittest.mock.patch("pcapi.routes.auth.discord.discord_connector.get_user_id", return_value="discord_user_id")
    @unittest.mock.patch("pcapi.routes.auth.discord.discord_connector.add_to_server")
    def test_discord_webhook_success(
        self, mock_add_to_server, mock_get_user_id, mock_retrieve_access_token, client, db_session
    ):
        user = users_factories.BeneficiaryFactory()
        discord_user = users_factories.DiscordUserFactory(user=user, discordId=None, hasAccess=True, isBanned=False)

        client.get(url_for("auth.discord_call_back", code="discord_code", state=str(user.id)))

        assert mock_retrieve_access_token.call_count == 1
        assert mock_retrieve_access_token.call_args[0][0] == "discord_code"

        assert mock_get_user_id.call_count == 1
        assert mock_get_user_id.call_args[0][0] == "access_token"

        assert mock_add_to_server.call_count == 1
        assert mock_add_to_server.call_args[0][0] == "access_token"
        assert mock_add_to_server.call_args[0][1] == "discord_user_id"

        db_session.refresh(discord_user)
        assert discord_user.discordId == "discord_user_id"

    @unittest.mock.patch(
        "pcapi.routes.auth.discord.discord_connector.retrieve_access_token", return_value="access_token"
    )
    @unittest.mock.patch("pcapi.routes.auth.discord.discord_connector.get_user_id", return_value="discord_user_id")
    @unittest.mock.patch("pcapi.routes.auth.discord.discord_connector.add_to_server")
    def test_has_access_is_false(self, _mock_add_to_server, _mock_get_user_id, _mock_retrieve_access_token, client):
        user = users_factories.BeneficiaryFactory()
        users_factories.DiscordUserFactory(user=user, discordId=None, hasAccess=False, isBanned=False)

        response = client.get(url_for("auth.discord_call_back", code="discord_code", state=str(user.id)))

        expected_query_params = (
            "Accès refusé au serveur Discord. Contacte le support pour plus d'informations".replace(" ", "%20")
            .replace("è", "%C3%A8")
            .replace("é", "%C3%A9")
        )

        assert response.status_code == 303
        assert f"/auth/discord/signin?error={expected_query_params}" in response.location

    @unittest.mock.patch(
        "pcapi.routes.auth.discord.discord_connector.retrieve_access_token", return_value="access_token"
    )
    @unittest.mock.patch("pcapi.routes.auth.discord.discord_connector.get_user_id", return_value="discord_user_id")
    @unittest.mock.patch("pcapi.routes.auth.discord.discord_connector.add_to_server")
    def test_discord_user_is_none(self, _mock_add_to_server, _mock_get_user_id, _mock_retrieve_access_token, client):
        user = users_factories.BeneficiaryFactory()

        response = client.get(url_for("auth.discord_call_back", code="discord_code", state=str(user.id)))

        expected_query_params = (
            "Accès refusé au serveur Discord. Contacte le support pour plus d'informations".replace(" ", "%20")
            .replace("è", "%C3%A8")
            .replace("é", "%C3%A9")
        )

        assert response.status_code == 303
        assert f"/auth/discord/signin?error={expected_query_params}" in response.location

    def test_account_anonymized_user_request_account_state(self, client):
        form_data = {"email": "user@test.com", "password": settings.TEST_DEFAULT_PASSWORD}
        users_factories.AnonymizedUserFactory(
            email=form_data["email"],
            password=form_data["password"],
        )
        response = self.post_to_endpoint(client, form=form_data)
        assert response.status_code == 200

        response_data = response.data.decode("utf-8")
        assert "Le compte a été anonymisé" in response_data

    def test_wrong_password(self, client):
        form_data = {"email": "user@test.com", "password": "wrong_password"}
        users_factories.AnonymizedUserFactory(
            email=form_data["email"],
            password=settings.TEST_DEFAULT_PASSWORD,
        )
        response = self.post_to_endpoint(client, form=form_data)
        assert response.status_code == 200

        response_data = response.data.decode("utf-8")
        assert "Identifiant ou Mot de passe incorrect" in response_data

    def test_account_deleted_account_state(self, client):
        form_data = {"email": "user@test.com", "password": settings.TEST_DEFAULT_PASSWORD}
        user = users_factories.UserFactory(email=form_data["email"], password=form_data["password"], isActive=False)
        history_factories.SuspendedUserActionHistoryFactory(user=user, reason=users_constants.SuspensionReason.DELETED)

        response = self.post_to_endpoint(client, form=form_data)
        assert response.status_code == 200

        response_data = response.data.decode("utf-8")
        assert "Le compte a été supprimé" in response_data

    def test_inactive_user_signin(self, client):
        form_data = {"email": "user@test.com", "password": settings.TEST_DEFAULT_PASSWORD}
        users_factories.BaseUserFactory(email=form_data["email"], password=form_data["password"])
        response = self.post_to_endpoint(client, form=form_data)
        assert response.status_code == 200

        response_data = response.data.decode("utf-8")
        assert (
            "L&#39;email n&#39;a pas été validé. Valide ton compte sur le pass Culture pour continuer" in response_data
        )

    def test_unknown_user_logs_in(self, client):
        form_data = {"email": "user@test.com", "password": settings.TEST_DEFAULT_PASSWORD}
        response = self.post_to_endpoint(client, form=form_data)
        assert response.status_code == 200

        response_data = response.data.decode("utf-8")
        assert "Identifiant ou Mot de passe incorrect" in response_data

    def test_user_without_password_logs_in(self, client):
        user = users_factories.UserFactory(password=None, isActive=True)
        form_data = {"email": user.email, "password": settings.TEST_DEFAULT_PASSWORD}
        response = self.post_to_endpoint(client, form=form_data)
        assert response.status_code == 200

        response_data = response.data.decode("utf-8")
        assert "Identifiant ou Mot de passe incorrect" in response_data

    def test_user_logs_in_with_missing_fields(self, client):
        form_data = {"email": "user@test.com"}
        response = self.post_to_endpoint(client, form=form_data)
        assert response.status_code == 200

        response_data = response.data.decode("utf-8")
        assert "Mot de passe : Information obligatoire" in response_data

    @unittest.mock.patch(
        "pcapi.routes.auth.discord.discord_connector.retrieve_access_token", return_value="access_token"
    )
    @unittest.mock.patch("pcapi.routes.auth.discord.discord_connector.get_user_id", return_value="discord_user_id")
    @unittest.mock.patch(
        "pcapi.routes.auth.discord.discord_connector.add_to_server",
        side_effect=requests.exceptions.HTTPError(),
    )
    def test_error_adding_user_to_server_rollbacks(
        self, _mock_add_to_server, _mock_get_user_id, _mock_retrieve_access_token, client, db_session
    ):
        user = users_factories.BeneficiaryFactory()
        discord_user = users_factories.DiscordUserFactory(user=user, discordId=None, hasAccess=True, isBanned=False)

        response = client.get(url_for("auth.discord_call_back", code="discord_code", state=str(user.id)))

        assert response.status_code == 303

        db_session.refresh(discord_user)
        assert discord_user.discordId is None
