from urllib.parse import urlparse

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from flask import g
from flask import url_for
import pytest

from pcapi import settings
from pcapi.core.history import factories as history_factories
from pcapi.core.testing import assert_num_queries
from pcapi.core.testing import override_settings
from pcapi.core.token import AsymetricToken
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
    def test_successfull_discord_signing(self, client):
        redirect_url_scheme = "https"
        redirect_url_netloc = "test.com"
        form_data = {
            "email": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "discord_id": "1234",
            "redirect_url": f"{redirect_url_scheme}://{redirect_url_netloc}",
        }
        user = users_factories.UserFactory(email=form_data["email"], password=form_data["password"], isActive=True)
        users_factories.DiscordUserFactory(user=user, discordId=None, hasAccess=True, isBanned=False)
        response = self.post_to_endpoint(client, form=form_data)
        assert response.status_code == 303

        url = urlparse(response.location)
        assert url.scheme == redirect_url_scheme
        assert url.netloc == redirect_url_netloc
        encoded_token = url.query.split("=")[1]
        token = AsymetricToken.load_without_checking(encoded_token, settings.DISCORD_JWT_PUBLIC_KEY)
        assert token.data["discord_id"] == form_data["discord_id"]
        assert token.data["status"] == "AUTHORIZED"

    @override_settings(DISCORD_JWT_PUBLIC_KEY=public_key_pem, DISCORD_JWT_PRIVATE_KEY=private_key_pem)
    def test_has_acess_is_false(self, client):
        redirect_url_scheme = "https"
        redirect_url_netloc = "test.com"
        form_data = {
            "email": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "discord_id": "1234",
            "redirect_url": f"{redirect_url_scheme}://{redirect_url_netloc}",
        }
        user = users_factories.UserFactory(email=form_data["email"], password=form_data["password"], isActive=True)
        users_factories.DiscordUserFactory(user=user, discordId=None, hasAccess=False, isBanned=False)
        response = self.post_to_endpoint(client, form=form_data)
        assert response.status_code == 303

        url = urlparse(response.location)
        assert url.scheme == redirect_url_scheme
        assert url.netloc == redirect_url_netloc
        encoded_token = url.query.split("=")[1]
        token = AsymetricToken.load_without_checking(encoded_token, settings.DISCORD_JWT_PUBLIC_KEY)
        assert token.data["discord_id"] == form_data["discord_id"]
        assert token.data["status"] == "UNAUTHORIZED"

    @override_settings(DISCORD_JWT_PUBLIC_KEY=public_key_pem, DISCORD_JWT_PRIVATE_KEY=private_key_pem)
    def test_discord_user_is_none(self, client):
        redirect_url_scheme = "https"
        redirect_url_netloc = "test.com"
        form_data = {
            "email": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "discord_id": "1234",
            "redirect_url": f"{redirect_url_scheme}://{redirect_url_netloc}",
        }
        users_factories.UserFactory(email=form_data["email"], password=form_data["password"], isActive=True)
        response = self.post_to_endpoint(client, form=form_data)
        assert response.status_code == 303

        url = urlparse(response.location)
        assert url.scheme == redirect_url_scheme
        assert url.netloc == redirect_url_netloc
        encoded_token = url.query.split("=")[1]
        token = AsymetricToken.load_without_checking(encoded_token, settings.DISCORD_JWT_PUBLIC_KEY)
        assert token.data["discord_id"] == form_data["discord_id"]
        assert token.data["status"] == "UNAUTHORIZED"

    @override_settings(DISCORD_JWT_PUBLIC_KEY=public_key_pem, DISCORD_JWT_PRIVATE_KEY=private_key_pem)
    def test_discord_user_is_active(self, client):
        redirect_url_scheme = "https"
        redirect_url_netloc = "test.com"
        form_data = {
            "email": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "discord_id": "1234",
            "redirect_url": f"{redirect_url_scheme}://{redirect_url_netloc}",
        }
        user = users_factories.UserFactory(email=form_data["email"], password=form_data["password"], isActive=True)
        users_factories.DiscordUserFactory(user=user, hasAccess=True, isBanned=False)
        response = self.post_to_endpoint(client, form=form_data)
        assert response.status_code == 303

        url = urlparse(response.location)
        assert url.scheme == redirect_url_scheme
        assert url.netloc == redirect_url_netloc
        encoded_token = url.query.split("=")[1]
        token = AsymetricToken.load_without_checking(encoded_token, settings.DISCORD_JWT_PUBLIC_KEY)
        assert token.data["discord_id"] == form_data["discord_id"]
        assert token.data["status"] == "ALREADY_ACTIVE"

    def test_account_anonymized_user_request_account_state(self, client):
        redirect_url_scheme = "https"
        redirect_url_netloc = "test.com"
        form_data = {
            "email": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "discord_id": "1234",
            "redirect_url": f"{redirect_url_scheme}://{redirect_url_netloc}",
        }
        users_factories.AnonymizedUserFactory(
            email=form_data["email"],
            password=form_data["password"],
        )
        response = self.post_to_endpoint(client, form=form_data)
        assert response.status_code == 200

    def test_wrong_password(self, client):
        redirect_url_scheme = "https"
        redirect_url_netloc = "test.com"
        form_data = {
            "email": "user@test.com",
            "password": "wrong_password",
            "discord_id": "1234",
            "redirect_url": f"{redirect_url_scheme}://{redirect_url_netloc}",
        }
        users_factories.AnonymizedUserFactory(
            email=form_data["email"],
            password=settings.TEST_DEFAULT_PASSWORD,
        )
        response = self.post_to_endpoint(client, form=form_data)
        assert response.status_code == 200

    def test_account_deleted_account_state(self, client):
        redirect_url_scheme = "https"
        redirect_url_netloc = "test.com"
        form_data = {
            "email": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "discord_id": "1234",
            "redirect_url": f"{redirect_url_scheme}://{redirect_url_netloc}",
        }
        user = users_factories.UserFactory(email=form_data["email"], password=form_data["password"], isActive=False)
        history_factories.SuspendedUserActionHistoryFactory(user=user, reason=users_constants.SuspensionReason.DELETED)

        response = self.post_to_endpoint(client, form=form_data)
        assert response.status_code == 200

    def test_allow_inactive_user_sign(self, client):
        redirect_url_scheme = "https"
        redirect_url_netloc = "test.com"
        form_data = {
            "email": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "discord_id": "1234",
            "redirect_url": f"{redirect_url_scheme}://{redirect_url_netloc}",
        }
        users_factories.AnonymizedUserFactory(email=form_data["email"], password=form_data["password"], isActive=False)
        response = self.post_to_endpoint(client, form=form_data)
        assert response.status_code == 200

    def test_unknown_user_logs_in(self, client, caplog):
        redirect_url_scheme = "https"
        redirect_url_netloc = "test.com"
        form_data = {
            "email": "user@test.com",
            "password": settings.TEST_DEFAULT_PASSWORD,
            "discord_id": "1234",
            "redirect_url": f"{redirect_url_scheme}://{redirect_url_netloc}",
        }
        response = self.post_to_endpoint(client, form=form_data)
        assert response.status_code == 200

    def test_user_without_password_logs_in(self, client, caplog):
        user = users_factories.UserFactory(password=None, isActive=True)
        redirect_url_scheme = "https"
        redirect_url_netloc = "test.com"
        form_data = {
            "email": user.email,
            "password": settings.TEST_DEFAULT_PASSWORD,
            "discord_id": "1234",
            "redirect_url": f"{redirect_url_scheme}://{redirect_url_netloc}",
        }
        response = self.post_to_endpoint(client, form=form_data)
        assert response.status_code == 200

    def test_user_logs_in_with_missing_fields(self, client):
        redirect_url_scheme = "https"
        redirect_url_netloc = "test.com"
        form_data = {
            "email": "user@test.com",
            "discord_id": "1234",
            "redirect_url": f"{redirect_url_scheme}://{redirect_url_netloc}",
        }
        response = self.post_to_endpoint(client, form=form_data)
        assert response.status_code == 200
