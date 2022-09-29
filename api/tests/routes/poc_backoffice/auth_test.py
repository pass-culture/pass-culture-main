from unittest.mock import patch

from flask import url_for
import pytest

from pcapi.core.permissions import factories as perm_factories
from pcapi.core.testing import override_features
from pcapi.core.testing import override_settings
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models


pytestmark = pytest.mark.usefixtures("db_session")


class LoginPageTest:
    @override_features(ENABLE_NEW_BACKOFFICE_POC=True)
    def test_view_login_page(self, client):  # type: ignore
        response = client.get(url_for("poc_backoffice_web.login"))

        assert response.status_code == 302
        assert response.location == url_for("poc_backoffice_web.home", _external=True)

    @override_features(ENABLE_NEW_BACKOFFICE_POC=True)
    @override_settings(GOOGLE_CLIENT_ID="some client id")
    @override_settings(GOOGLE_CLIENT_SECRET="some client secret")
    def test_view_login_page_with_google_credentials_set(self, client):  # type: ignore
        response = client.get(url_for("poc_backoffice_web.login"))

        assert response.status_code == 302
        assert "google.com" in response.location

    @override_features(ENABLE_NEW_BACKOFFICE_POC=False)
    def test_redirects_to_unauthorized_if_ff_disabled(self, client):  # type: ignore
        response = client.get(url_for("poc_backoffice_web.login"))

        assert response.status_code == 302
        assert response.location == url_for("poc_backoffice_web.unauthorized", _external=True)


class UnauthorizedPageTest:
    def test_renders(self, client):  # type: ignore
        response = client.get(url_for("poc_backoffice_web.unauthorized"))
        assert response.status_code == 200


class AuthorizePageTest:
    @override_features(ENABLE_NEW_BACKOFFICE_POC=True)
    @patch("pcapi.routes.poc_backoffice.auth.oauth.google.parse_id_token")
    @patch("pcapi.routes.poc_backoffice.auth.oauth.google.authorize_access_token")
    def test_authorize(self, mock_authorize_access_token, mock_parse_id_token, client):  # type: ignore
        mock_parse_id_token.return_value = {
            "email": "email@example.com",
            "name": "Name",
            "family_name": "FamilyName",
            "given_name": "GivenName",
        }

        response = client.get(url_for("poc_backoffice_web.authorize"))

        assert response.status_code == 302
        assert response.location == url_for("poc_backoffice_web.home", _external=True)

    @override_features(ENABLE_NEW_BACKOFFICE_POC=True)
    @override_settings(IS_TESTING=False)
    @override_settings(IS_DEV=False)
    @override_settings(GOOGLE_CLIENT_ID="some client id")
    @override_settings(GOOGLE_CLIENT_SECRET="some client secret")
    @patch("pcapi.routes.poc_backoffice.auth.fetch_user_permissions_from_google_workspace")
    @patch("pcapi.routes.poc_backoffice.auth.oauth.google.parse_id_token")
    @patch("pcapi.routes.poc_backoffice.auth.oauth.google.authorize_access_token")
    def test_authorize_with_google_credentials(  # type: ignore
        self, mock_authorize_access_token, mock_parse_id_token, mock_fetch_user_permissions, client
    ):
        user = users_factories.UserFactory()
        expected_permissions = [perm_factories.PermissionFactory()]

        mock_parse_id_token.return_value = {
            "email": user.email,
            "name": "Name",
            "family_name": "FamilyName",
            "given_name": "GivenName",
        }

        mock_fetch_user_permissions.return_value = expected_permissions

        response = client.get(url_for("poc_backoffice_web.authorize"))

        assert response.status_code == 302
        assert response.location == url_for("poc_backoffice_web.home", _external=True)

        user = users_models.User.query.get(user.id)
        assert user.backoffice_permissions == expected_permissions

    @override_features(ENABLE_NEW_BACKOFFICE_POC=True)
    @override_settings(IS_TESTING=False)
    @override_settings(IS_DEV=False)
    @override_settings(GOOGLE_CLIENT_ID="some client id")
    @override_settings(GOOGLE_CLIENT_SECRET="some client secret")
    @patch("pcapi.routes.poc_backoffice.auth.oauth.google.parse_id_token")
    @patch("pcapi.routes.poc_backoffice.auth.oauth.google.authorize_access_token")
    def test_user_not_found_with_google_credentials(  # type: ignore
        self, mock_authorize_access_token, mock_parse_id_token, client
    ):
        mock_parse_id_token.return_value = {
            "email": "email@example.com",
            "name": "Name",
            "family_name": "FamilyName",
            "given_name": "GivenName",
        }

        response = client.get(url_for("poc_backoffice_web.authorize"))

        assert response.status_code == 302
        assert response.location == url_for("poc_backoffice_web.user_not_found", _external=True)

    @override_features(ENABLE_NEW_BACKOFFICE_POC=False)
    def test_unauthorized_when_ff_is_disabled(self, client):  # type: ignore
        response = client.get(url_for("poc_backoffice_web.authorize"))

        assert response.status_code == 302
        assert response.location == url_for("poc_backoffice_web.unauthorized", _external=True)


class LogoutPageTest:
    def test_renders(self, client):  # type: ignore
        response = client.post(url_for("poc_backoffice_web.logout"))
        assert response.status_code == 302
        assert response.location == url_for("poc_backoffice_web.home", _external=True)


class UserNotFoundPageTest:
    def test_renders(self, client):  # type: ignore
        response = client.get(url_for("poc_backoffice_web.user_not_found"))
        assert response.status_code == 200
