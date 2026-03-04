import unittest
from unittest.mock import patch
from urllib.parse import unquote

import pytest
import time_machine
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from flask import g
from flask import url_for

from pcapi import settings
from pcapi.connectors import discord as discord_connector
from pcapi.core.history import factories as history_factories
from pcapi.core.testing import assert_num_queries
from pcapi.core.users import constants as users_constants
from pcapi.core.users import factories as users_factories
from pcapi.core.users import utils as users_utils
from pcapi.core.users.models import DiscordUser
from pcapi.models import db
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

    def _build_signed_state(self, user_id):
        # Access to the private _sign_state is intentional: tests need a valid signed state
        # without going through the full signin flow.
        return discord_connector._sign_state(user_id)

    @pytest.mark.settings(DISCORD_JWT_PUBLIC_KEY=public_key_pem, DISCORD_JWT_PRIVATE_KEY=private_key_pem)
    def test_build_discord_redirection_uri(self):
        uri = discord_connector.build_discord_redirection_uri(1)
        assert uri.startswith(
            f"https://discord.com/api/oauth2/authorize?client_id={discord_connector.DISCORD_CLIENT_ID}"
        )
        assert "&state=" in uri
        # Verify the state is a signed RS256 JWT containing the user_id
        state = uri.split("&state=")[1]
        payload = users_utils.decode_jwt_token_rs256(state, public_key=settings.DISCORD_JWT_PUBLIC_KEY)
        assert payload["user_id"] == 1
        assert "exp" in payload

    @pytest.mark.settings(DISCORD_JWT_PUBLIC_KEY=public_key_pem, DISCORD_JWT_PRIVATE_KEY=private_key_pem)
    def test_redirect_to_discord_on_post(self, client):
        form_data = {
            "email": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "recaptcha_token": "recaptcha_token",
        }
        _user = users_factories.BeneficiaryFactory(
            email=form_data["email"], password=form_data["password"], isActive=True
        )

        response = self.post_to_endpoint(client, form=form_data)

        assert response.status_code == 302
        assert response.location.startswith("https://discord.com/api/oauth2/authorize")

    @pytest.mark.settings(RECAPTCHA_IGNORE_VALIDATION=0)
    @patch("pcapi.connectors.api_recaptcha.get_token_validation_and_score")
    def test_discord_recaptcha_does_not_pass(self, mocked_recaptcha_validation, client):
        mocked_recaptcha_validation.return_value = {"success": False, "error-codes": ["error"]}
        form_data = {
            "email": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "recaptcha_token": "recaptcha_token",
        }

        response = self.post_to_endpoint(client, form=form_data)
        assert response.status_code == 200

        response_data = response.data.decode("utf-8")
        assert "La vérification a échoué. Recharge la page et réessaie" in response_data

    @pytest.mark.settings(DISCORD_JWT_PUBLIC_KEY=public_key_pem, DISCORD_JWT_PRIVATE_KEY=private_key_pem)
    @unittest.mock.patch(
        "pcapi.routes.auth.discord.discord_connector.retrieve_access_token", return_value="access_token"
    )
    def test_callback_redirects_to_success_url(self, mock_retrieve_access_token, client):
        user = users_factories.BeneficiaryFactory()
        signed_state = self._build_signed_state(user.id)

        response = client.get(url_for("auth.discord_call_back", code="discord_code", state=signed_state))

        assert mock_retrieve_access_token.call_count == 1
        assert mock_retrieve_access_token.call_args[0][0] == "discord_code"

        assert response.status_code == 303

    @pytest.mark.settings(DISCORD_JWT_PUBLIC_KEY=public_key_pem)
    def test_callback_rejects_invalid_state(self, client):
        response = client.get(url_for("auth.discord_call_back", code="discord_code", state="forged_user_id"))

        assert response.status_code == 303
        assert "lien invalide ou expir" in unquote(response.location)

    @pytest.mark.settings(DISCORD_JWT_PUBLIC_KEY=public_key_pem, DISCORD_JWT_PRIVATE_KEY=private_key_pem)
    def test_callback_rejects_expired_state(self, client):
        user = users_factories.BeneficiaryFactory()
        with time_machine.travel("2020-01-01"):
            expired_state = self._build_signed_state(user.id)

        response = client.get(url_for("auth.discord_call_back", code="discord_code", state=expired_state))

        assert response.status_code == 303
        assert "lien invalide ou expir" in unquote(response.location)

    def test_callback_rejects_missing_state(self, client):
        response = client.get(url_for("auth.discord_call_back", code="discord_code"))

        assert response.status_code == 303
        assert "état de la requête non récupéré" in unquote(response.location)

    @unittest.mock.patch("pcapi.routes.auth.discord.discord_connector.get_user_id", return_value="discord_user_id")
    @unittest.mock.patch("pcapi.routes.auth.discord.discord_connector.add_to_server")
    def test_discord_credentials_success_page(self, mock_add_to_server, mock_get_user_id, client, db_session):
        user = users_factories.BeneficiaryFactory()
        discord_user = users_factories.DiscordUserFactory(user=user, discordId=None, hasAccess=True, isBanned=False)

        client.get(url_for("auth.discord_success", user_id=str(user.id), access_token="access_token"))

        assert mock_get_user_id.call_count == 1
        assert mock_get_user_id.call_args[0][0] == "access_token"

        assert mock_add_to_server.call_count == 1
        assert mock_add_to_server.call_args[0][0] == "access_token"
        assert mock_add_to_server.call_args[0][1] == "discord_user_id"

        db.session.refresh(discord_user)
        assert discord_user.discordId == "discord_user_id"

    @unittest.mock.patch(
        "pcapi.routes.auth.discord.discord_connector.get_user_id",
        side_effect=requests.exceptions.HTTPError(),
    )
    def test_xss_access_token_is_encoded_in_retry_page(self, _mock_get_user_id, client):
        user = users_factories.BeneficiaryFactory()
        malicious_token = "';alert(1)//"

        response = client.get(url_for("auth.discord_success", user_id=str(user.id), access_token=malicious_token))

        assert response.status_code == 200
        body = response.data.decode("utf-8")
        assert malicious_token not in body
        assert "onclick" not in body

    @unittest.mock.patch("pcapi.routes.auth.discord.discord_connector.get_user_id", return_value="discord_user_id")
    @unittest.mock.patch(
        "pcapi.routes.auth.discord.discord_connector.add_to_server", side_effect=requests.exceptions.HTTPError()
    )
    def test_error_when_adding_to_server(self, _mock_add_to_server, _mock_get_user_id, client):
        user = users_factories.BeneficiaryFactory()
        users_factories.DiscordUserFactory(user=user, discordId=None, hasAccess=True, isBanned=False)

        response = client.get(url_for("auth.discord_success", user_id=str(user.id), access_token="access_token"))

        assert response.status_code == 200
        assert (
            "Erreur lors de l&#39;ajout au serveur Discord: réessaye en cliquant sur le bouton ci-dessous"
            in response.data.decode("utf-8")
        )

    def test_success_without_session_redirects_with_error(self, client):
        response = client.get(url_for("auth.discord_success"))

        assert response.status_code == 303
        assert "session invalide ou expir" in unquote(response.location)

    def test_account_anonymized_user_request_account_state(self, client):
        form_data = {
            "email": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "recaptcha_token": "recaptcha_token",
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
        form_data = {"email": "user@test.com", "password": "wrong_password", "recaptcha_token": "recaptcha_token"}
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
            "recaptcha_token": "recaptcha_token",
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
            "recaptcha_token": "recaptcha_token",
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
            "recaptcha_token": "recaptcha_token",
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
            "recaptcha_token": "recaptcha_token",
        }
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
    @pytest.mark.settings(DISCORD_JWT_PUBLIC_KEY=public_key_pem, DISCORD_JWT_PRIVATE_KEY=private_key_pem)
    def test_error_adding_user_to_server_rollbacks(
        self, _mock_add_to_server, _mock_get_user_id, _mock_retrieve_access_token, client, db_session
    ):
        user = users_factories.BeneficiaryFactory()
        discord_user = users_factories.DiscordUserFactory(user=user, discordId=None, hasAccess=True, isBanned=False)
        signed_state = self._build_signed_state(user.id)

        response = client.get(url_for("auth.discord_call_back", code="discord_code", state=signed_state))

        assert response.status_code == 303

        db.session.refresh(discord_user)
        assert discord_user.discordId is None

    @unittest.mock.patch("pcapi.routes.auth.discord.discord_connector.get_user_id", return_value="discord_user_id")
    @unittest.mock.patch(
        "pcapi.routes.auth.discord.discord_connector.add_to_server", side_effect=requests.exceptions.HTTPError()
    )
    def test_discord_user_has_access_if_beneficiary(
        self, _mock_discord_getter, _mock_add_to_server, client, db_session
    ):
        user = users_factories.BeneficiaryFactory()

        response = client.get(url_for("auth.discord_success", user_id=str(user.id), access_token="access_token"))
        assert response.status_code == 200

        created_discord_link = db.session.query(DiscordUser).filter_by(userId=user.id).first()
        assert created_discord_link.hasAccess

    @unittest.mock.patch("pcapi.routes.auth.discord.discord_connector.get_user_id", return_value="discord_user_id")
    @unittest.mock.patch(
        "pcapi.routes.auth.discord.discord_connector.add_to_server", side_effect=requests.exceptions.HTTPError()
    )
    def test_discord_user_has_not_access_if_non_beneficiary(
        self, _mock_discord_getter, _mock_add_to_server, client, db_session
    ):
        non_beneficiary = users_factories.UserFactory()

        response = client.get(
            url_for("auth.discord_success", user_id=str(non_beneficiary.id), access_token="access_token")
        )
        assert response.status_code == 303

        assert db.session.query(DiscordUser).filter_by(userId=non_beneficiary.id).count() == 0

    @unittest.mock.patch("pcapi.routes.auth.discord.discord_connector.get_user_id", return_value="discord_user_id")
    @unittest.mock.patch(
        "pcapi.routes.auth.discord.discord_connector.add_to_server", side_effect=requests.exceptions.HTTPError()
    )
    def test_discord_user_has_not_access_if_beneficiary_under_17(
        self, _mock_discord_getter, _mock_add_to_server, client, db_session
    ):
        not_eligible_user = users_factories.BeneficiaryFactory(age=16)

        response = client.get(
            url_for("auth.discord_success", user_id=str(not_eligible_user.id), access_token="access_token")
        )
        assert response.status_code == 303

        assert db.session.query(DiscordUser).filter_by(userId=not_eligible_user.id).count() == 0

    @unittest.mock.patch("pcapi.routes.auth.discord.discord_connector.get_user_id", return_value="discord_user_id")
    @unittest.mock.patch("pcapi.routes.auth.discord.discord_connector.add_to_server")
    def test_discord_account_already_linked_to_same_user(
        self, mock_add_to_server, mock_get_user_id, client, db_session
    ):
        user = users_factories.BeneficiaryFactory()
        discord_user = users_factories.DiscordUserFactory(
            user=user, discordId="discord_user_id", hasAccess=True, isBanned=False
        )

        response = client.get(url_for("auth.discord_success", user_id=str(user.id), access_token="access_token"))
        assert response.status_code == 303

        assert mock_get_user_id.call_count == 1
        assert mock_get_user_id.call_args[0][0] == "access_token"

        assert mock_add_to_server.call_count == 1
        assert mock_add_to_server.call_args[0][0] == "access_token"
        assert mock_add_to_server.call_args[0][1] == "discord_user_id"

        db.session.refresh(discord_user)
        assert discord_user.discordId == "discord_user_id"

    @unittest.mock.patch("pcapi.routes.auth.discord.discord_connector.get_user_id", return_value="discord_user_id")
    @unittest.mock.patch("pcapi.routes.auth.discord.discord_connector.add_to_server")
    def test_discord_account_already_linked_to_another_user(
        self, mock_add_to_server, mock_get_user_id, client, db_session
    ):
        user = users_factories.BeneficiaryFactory()
        another_user = users_factories.BeneficiaryFactory()
        users_factories.DiscordUserFactory(user=user, discordId="discord_user_id", hasAccess=True, isBanned=False)

        response = client.get(
            url_for("auth.discord_success", user_id=str(another_user.id), access_token="access_token")
        )
        assert response.status_code == 303
        assert "Impossible d" in unquote(response.location)

        assert mock_get_user_id.call_count == 1
        assert mock_get_user_id.call_args[0][0] == "access_token"

        assert mock_add_to_server.call_count == 0

    @unittest.mock.patch("pcapi.routes.auth.discord.discord_connector.get_user_id", return_value="discord_user_id")
    def test_association_errors_return_generic_message(self, _mock_get_user_id, client, db_session):
        """All association errors should return the same generic message to prevent information leakage."""
        non_beneficiary = users_factories.UserFactory()

        response = client.get(
            url_for("auth.discord_success", user_id=str(non_beneficiary.id), access_token="access_token")
        )
        assert response.status_code == 303
        assert "Impossible" in unquote(response.location)
        assert "Contacte le support" in unquote(response.location)

    @pytest.mark.features(DISCORD_ENABLE_NEW_ACCESS=False)
    def test_discord_signin_disabled(self, client):
        response = client.get(url_for("auth.discord_signin"))
        assert response.status_code == 200
        assert "L'accès au serveur Discord du pass Culture est désactivé" in response.data.decode()

    @pytest.mark.features(DISCORD_ENABLE_NEW_ACCESS=False)
    def test_discord_signin_disabled_post(self, client):
        form_data = {
            "email": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
        }
        users_factories.BeneficiaryFactory(email=form_data["email"], password=form_data["password"], isActive=True)

        response = self.post_to_endpoint(client, form=form_data)

        assert response.status_code == 200
        assert "L'accès au serveur Discord du pass Culture est désactivé" in response.data.decode()
