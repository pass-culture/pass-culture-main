from unittest.mock import patch

from flask import g
from flask import url_for
import pytest

from pcapi.core.permissions import models as perm_models
from pcapi.core.testing import override_features
from pcapi.core.testing import override_settings
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice_v3,
]


class LoginPageTest:
    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_view_login_page(self, client, app):  # type: ignore
        response = client.get(url_for("backoffice_v3_web.login"))

        assert response.status_code == 302
        assert response.location == url_for("backoffice_v3_web.home", _external=True)

    @override_features(WIP_ENABLE_BACKOFFICE_V3=False)
    def test_redirects_to_not_enabled_if_ff_disabled(self, client):  # type: ignore
        response = client.get(url_for("backoffice_v3_web.login"))
        assert response.status_code == 400


class AuthorizePageTest:
    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    @patch("pcapi.routes.backoffice_v3.auth.oauth.google.parse_id_token")
    @patch("pcapi.routes.backoffice_v3.auth.oauth.google.authorize_access_token")
    def test_authorize(self, mock_authorize_access_token, mock_parse_id_token, client):  # type: ignore
        mock_parse_id_token.return_value = {
            "email": "email@example.com",
            "name": "Name",
            "family_name": "FamilyName",
            "given_name": "GivenName",
        }

        response = client.get(url_for("backoffice_v3_web.authorize"))

        assert response.status_code == 302
        assert response.location == url_for("backoffice_v3_web.home", _external=True)

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    @override_settings(IS_TESTING=False)
    @override_settings(IS_DEV=False)
    @override_settings(GOOGLE_CLIENT_ID="some client id")
    @override_settings(GOOGLE_CLIENT_SECRET="some client secret")
    @patch("pcapi.routes.backoffice_v3.auth.fetch_user_roles_from_google_workspace")
    @patch("pcapi.routes.backoffice_v3.auth.oauth.google.parse_id_token")
    @patch("pcapi.routes.backoffice_v3.auth.oauth.google.authorize_access_token")
    def test_authorize_with_google_credentials(  # type: ignore
        self,
        mock_authorize_access_token,
        mock_parse_id_token,
        mock_fetch_user_roles,
        client,
        roles_with_permissions,
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

        response = client.get(url_for("backoffice_v3_web.authorize"))

        assert response.status_code == 302
        assert response.location == url_for("backoffice_v3_web.home", _external=True)

        user = users_models.User.query.get(user.id)
        user_role_names = {role.name for role in user.backoffice_profile.roles}
        expected_role_names = {role.value for role in expected_roles}

        assert user_role_names == expected_role_names

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    @override_settings(IS_TESTING=False)
    @override_settings(IS_DEV=False)
    @override_settings(GOOGLE_CLIENT_ID="some client id")
    @override_settings(GOOGLE_CLIENT_SECRET="some client secret")
    @patch("pcapi.routes.backoffice_v3.auth.oauth.google.parse_id_token")
    @patch("pcapi.routes.backoffice_v3.auth.oauth.google.authorize_access_token")
    def test_user_not_found_with_google_credentials(  # type: ignore
        self, mock_authorize_access_token, mock_parse_id_token, client
    ):
        mock_parse_id_token.return_value = {
            "email": "email@example.com",
            "name": "Name",
            "family_name": "FamilyName",
            "given_name": "GivenName",
        }

        response = client.get(url_for("backoffice_v3_web.authorize"))

        assert response.status_code == 302
        assert response.location == url_for("backoffice_v3_web.user_not_found", _external=True)

    @override_features(WIP_ENABLE_BACKOFFICE_V3=False)
    def test_unauthorized_when_ff_is_disabled(self, client):  # type: ignore
        response = client.get(url_for("backoffice_v3_web.authorize"))

        assert response.status_code == 400


class LogoutTest:
    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_logout_success(self, client):  # type: ignore
        user = users_factories.UserFactory()

        # fetch home page to get the logout csrf token
        response = client.get(url_for("backoffice_v3_web.home"))
        assert response.status_code == 200

        url = url_for("backoffice_v3_web.logout")
        response = client.with_bo_session_auth(user).post(url, form={"csrf_token": g.get("csrf_token", "")})

        assert response.status_code == 302
        assert response.location == url_for("backoffice_v3_web.home", _external=True)

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_no_csrf_token(self, client):  # type: ignore
        response = client.post(url_for("backoffice_v3_web.logout"))
        assert response.status_code == 400


class UserNotFoundPageTest:
    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_renders(self, client):  # type: ignore
        response = client.get(url_for("backoffice_v3_web.user_not_found"))
        assert response.status_code == 200
