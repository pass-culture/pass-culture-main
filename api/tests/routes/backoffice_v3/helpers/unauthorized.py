from flask import g
from flask import url_for
import pytest

from pcapi.core.testing import override_features
from pcapi.core.users import factories as users_factories

from . import base


pytestmark = pytest.mark.usefixtures("db_session")


class UnauthorizedHelper(base.BaseHelper):
    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_missing_permission(self, client):  # type: ignore
        user = users_factories.UserFactory(isActive=True)

        authenticated_client = client.with_session_auth(user.email)
        response = authenticated_client.get(self.path)

        assert response.status_code == 403

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_not_logged_in(self, client):  # type: ignore
        response = client.get(self.path)
        assert response.status_code == 403

    @override_features(WIP_ENABLE_BACKOFFICE_V3=False)
    def test_ff_disabled(self, client):  # type: ignore
        response = client.get(self.path)
        assert response.status_code == 400


@pytest.mark.skip(reason="csrf temporarily deactivated")
class UnauthorizedHelperWithCsrf(UnauthorizedHelper):
    @property
    def method(self):
        return "post"

    @property
    def form(self):
        return {"csrf_token": g.get("csrf_token", None)}

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_missing_permission(self, client):  # type: ignore
        user = users_factories.UserFactory(isActive=True)

        self.fetch_csrf_token(client)

        authenticated_client = client.with_session_auth(user.email)
        client_method = getattr(authenticated_client, self.method)

        response = client_method(self.path, form=self.form)

        assert response.status_code == 403

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_not_logged_in(self, client):  # type: ignore
        self.fetch_csrf_token(client)

        client_method = getattr(client, self.method)
        response = client_method(self.path, form=self.form)

        assert response.status_code == 403

    @override_features(WIP_ENABLE_BACKOFFICE_V3=False)
    def test_ff_disabled(self, client):  # type: ignore
        client_method = getattr(client, self.method)
        response = client_method(self.path)

        assert response.status_code == 400

    def fetch_csrf_token(self, client):
        # will generate a csrf token (for the logout button)
        client.get(url_for("backoffice_v3_web.home"))


@pytest.mark.skip(reason="csrf temporarily deactivated")
class MissingCSRFHelper(base.BaseHelper):
    @property
    def method(self):
        return "post"

    @property
    def form(self):
        return {}

    @override_features(WIP_ENABLE_BACKOFFICE_V3=True)
    def test_missing_csrf_token(self, client):  # type: ignore
        user = users_factories.UserFactory(isActive=True)

        authenticated_client = client.with_session_auth(user.email)
        client_method = getattr(authenticated_client, self.method)

        response = client_method(self.path, form=self.form)
        assert response.status_code == 400
