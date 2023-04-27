import logging
from unittest.mock import patch

from flask import url_for
import pytest

from pcapi.core.permissions import models as perm_models
from pcapi.core.testing import override_settings
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models

from .helpers.post import PostEndpointWithoutPermissionHelper


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice_v3,
]


class LoginPageTest:
    def test_view_login_page(self, client, app):
        response = client.get(url_for("backoffice_v3_web.login"))

        assert response.status_code == 302
        assert response.location == url_for("backoffice_v3_web.home", _external=True)


class AuthorizePageTest:
    @patch("pcapi.routes.backoffice_v3.auth.oauth.google.parse_id_token")
    @patch("pcapi.routes.backoffice_v3.auth.oauth.google.authorize_access_token")
    def test_authorize(self, mock_authorize_access_token, mock_parse_id_token, client):
        mock_parse_id_token.return_value = {
            "email": "email@example.com",
            "name": "Name",
            "family_name": "FamilyName",
            "given_name": "GivenName",
        }

        response = client.get(url_for("backoffice_v3_web.authorize"))

        assert response.status_code == 302
        assert response.location == url_for("backoffice_v3_web.home", _external=True)

    @override_settings(IS_TESTING=False)
    @override_settings(IS_DEV=False)
    @override_settings(GOOGLE_CLIENT_ID="some client id")
    @override_settings(GOOGLE_CLIENT_SECRET="some client secret")
    @patch("pcapi.routes.backoffice_v3.auth.fetch_user_roles_from_google_workspace")
    @patch("pcapi.routes.backoffice_v3.auth.oauth.google.parse_id_token")
    @patch("pcapi.routes.backoffice_v3.auth.oauth.google.authorize_access_token")
    def test_authorize_with_google_credentials(
        self,
        mock_authorize_access_token,
        mock_parse_id_token,
        mock_fetch_user_roles,
        client,
        roles_with_permissions,
        caplog,
    ):
        user = users_factories.UserFactory()
        expected_roles = [perm_models.Roles.ADMIN]

        mock_parse_id_token.return_value = {
            "email": user.email,
            "name": "Name",
            "family_name": "FamilyName",
            "given_name": "GivenName",
        }

        mock_fetch_user_roles.return_value = expected_roles

        with caplog.at_level(logging.INFO):
            response = client.get(url_for("backoffice_v3_web.authorize"))

        assert response.status_code == 302
        assert response.location == url_for("backoffice_v3_web.home", _external=True)
        assert "Successful authentication attempt" in caplog.messages

        user = users_models.User.query.get(user.id)
        user_role_names = {role.name for role in user.backoffice_profile.roles}
        expected_role_names = {role.value for role in expected_roles}

        assert user_role_names == expected_role_names

    @override_settings(IS_TESTING=False)
    @override_settings(IS_DEV=False)
    @override_settings(GOOGLE_CLIENT_ID="some client id")
    @override_settings(GOOGLE_CLIENT_SECRET="some client secret")
    @patch("pcapi.routes.backoffice_v3.auth.oauth.google.parse_id_token")
    @patch("pcapi.routes.backoffice_v3.auth.oauth.google.authorize_access_token")
    def test_user_not_found_with_google_credentials(
        self, mock_authorize_access_token, mock_parse_id_token, client, caplog
    ):
        mock_parse_id_token.return_value = {
            "email": "email@example.com",
            "name": "Name",
            "family_name": "FamilyName",
            "given_name": "GivenName",
        }

        with caplog.at_level(logging.INFO):
            response = client.get(url_for("backoffice_v3_web.authorize"))

        assert response.status_code == 302
        assert response.location == url_for("backoffice_v3_web.user_not_found", _external=True)
        assert "Failed authentication attempt" in caplog.messages


class LogoutTest(PostEndpointWithoutPermissionHelper):
    endpoint = "backoffice_v3_web.logout"
    needed_permission = None

    def test_logout_success(self, authenticated_client):
        response = self.post_to_endpoint(authenticated_client)

        assert response.status_code == 302
        assert response.location == url_for("backoffice_v3_web.home", _external=True)


class UserNotFoundPageTest:
    def test_renders(self, client):
        response = client.get(url_for("backoffice_v3_web.user_not_found"))
        assert response.status_code == 200
