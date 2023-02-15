import abc

from flask import g
from flask import url_for
import pytest

from pcapi.core.permissions import factories as perm_factories
import pcapi.core.permissions.models as perm_models
from pcapi.core.users import factories as users_factories
import pcapi.core.users.models as users_models

from . import base


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice_v3,
]


class UnauthorizedHelperBase(base.BaseHelper, metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def needed_permission(self) -> perm_models.Permissions:
        pass

    @abc.abstractmethod
    def test_missing_permission(self, client):  # type: ignore
        pass

    @abc.abstractmethod
    def test_no_backoffice_profile(self, client):  # type: ignore
        pass

    @abc.abstractmethod
    def test_not_logged_in(self, client):  # type: ignore
        pass

    def setup_user(self) -> users_models.User:
        user = users_factories.UserFactory(isActive=True)

        # Create a unique test role which has all permissions but the one required
        perms_in_db = {perm.name: perm for perm in perm_models.Permission.query.all()}
        role = perm_factories.RoleFactory(
            permissions=[perms_in_db[perm.name] for perm in perm_models.Permissions if perm != self.needed_permission]
        )

        user.backoffice_profile = perm_models.BackOfficeUserProfile(user=user, roles=[role])

        assert len(user.backoffice_profile.permissions) == len(perm_models.Permissions) - 1
        assert self.needed_permission not in user.backoffice_profile.permissions

        return user


class UnauthorizedHelper(UnauthorizedHelperBase):
    def test_missing_permission(self, client):  # type: ignore
        user = self.setup_user()

        authenticated_client = client.with_bo_session_auth(user)
        response = authenticated_client.get(self.path)

        assert response.status_code == 403

    def test_no_backoffice_profile(self, client):  # type: ignore
        user = users_factories.UserFactory(isActive=True)

        authenticated_client = client.with_bo_session_auth(user)
        response = authenticated_client.get(self.path)

        assert response.status_code == 403

    def test_not_logged_in(self, client):  # type: ignore
        response = getattr(client, self.http_method)(self.path)
        assert response.status_code in (302, 303)

        expected_url = url_for("backoffice_v3_web.home", _external=True)
        assert response.location == expected_url


class UnauthorizedHelperWithCsrf(UnauthorizedHelperBase):
    @property
    def method(self) -> str:
        return "post"

    @property
    def form(self) -> dict:
        return {"csrf_token": g.get("csrf_token", None)}

    def test_missing_permission(self, client):  # type: ignore
        user = self.setup_user()

        self.fetch_csrf_token(client)

        authenticated_client = client.with_bo_session_auth(user)
        client_method = getattr(authenticated_client, self.method)

        response = client_method(self.path, form=self.form)

        assert response.status_code == 403

    def test_no_backoffice_profile(self, client):  # type: ignore
        user = users_factories.UserFactory(isActive=True)

        self.fetch_csrf_token(client)

        authenticated_client = client.with_bo_session_auth(user)
        client_method = getattr(authenticated_client, self.method)

        response = client_method(self.path, form=self.form)

        assert response.status_code == 403

    def test_not_logged_in(self, client):  # type: ignore
        self.fetch_csrf_token(client)

        client_method = getattr(client, self.method)
        response = client_method(self.path, form=self.form)

        assert response.status_code in (302, 303)

        expected_url = url_for("backoffice_v3_web.home", _external=True)
        assert response.location == expected_url

    def fetch_csrf_token(self, client):  # type: ignore
        # will generate a csrf token (for the logout button)
        client.get(url_for("backoffice_v3_web.home"))


class MissingCSRFHelper(base.BaseHelper):
    @property
    def method(self) -> str:
        return "post"

    @property
    def form(self) -> dict:
        return {}

    def test_missing_csrf_token(self, client):  # type: ignore
        user = users_factories.UserFactory(isActive=True)

        authenticated_client = client.with_bo_session_auth(user)
        client_method = getattr(authenticated_client, self.method)

        response = client_method(self.path, form=self.form)
        assert response.status_code == 400
