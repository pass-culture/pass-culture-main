from base64 import b64encode
from urllib.parse import unquote_plus

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
        if hasattr(self, "custom_redirect"):
            expected_urls = [url_for(self.custom_redirect, _external=True)]
        else:
            expected_urls = [
                url_for(
                    "backoffice_v3_web.home",
                    _external=True,
                    redirect=b64encode(unquote_plus(self.path).encode() + b"?"),
                ),
                url_for(
                    "backoffice_v3_web.home",
                    _external=True,
                    redirect=b64encode(self.path.encode() + b"?"),
                ),
                url_for(
                    "backoffice_v3_web.home",
                    _external=True,
                    redirect=b64encode(unquote_plus(self.path).encode()),
                ),
                url_for(
                    "backoffice_v3_web.home",
                    _external=True,
                    redirect=b64encode(self.path.encode()),
                ),
            ]
        assert response.location in expected_urls
