from flask import url_for

from pcapi.core.users import factories as users_factories

from .unauthorized import UnauthorizedHelperBase


class GetEndpointHelper(UnauthorizedHelperBase):
    def test_missing_permission(self, client):
        user = self.setup_user()

        authenticated_client = client.with_bo_session_auth(user)
        response = authenticated_client.get(self.path)

        assert response.status_code == 403

    def test_no_backoffice_profile(self, client):
        user = users_factories.UserFactory()

        authenticated_client = client.with_bo_session_auth(user)
        response = authenticated_client.get(self.path)

        assert response.status_code == 403

    def test_not_logged_in(self, client):
        response = getattr(client, self.http_method)(self.path)
        assert response.status_code in (302, 303)
        assert response.location == url_for("backoffice_v3_web.home", _external=True)
