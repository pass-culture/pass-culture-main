import re

from flask import url_for

from pcapi.core.testing import assert_num_queries
from pcapi.core.users import factories as users_factories

from . import base
from . import unauthorized


class PostEndpointWithoutPermissionHelper(base.BaseHelper):
    """
    Can be used when no permission is required
    """

    # Number of queries to fetch csrf token from homepage
    # Same as expected_num_queries in HomePageTest
    fetch_csrf_num_queries = 3

    @property
    def method(self) -> str:
        return "post"

    def form(self, client) -> dict:
        return {"csrf_token": getattr(client, "csrf_token", None)}

    def fetch_csrf(self, client) -> str:
        response = client.get(url_for("backoffice_web.home"))
        match = re.search(r'<meta name="csrf-token"\n *content="([^"]+)">', response.text)
        return match.groups()[0]

    def post_to_endpoint(
        self,
        client,
        form=None,
        headers=None,
        follow_redirects=False,
        expected_num_queries: int | None = None,
        **url_kwargs,
    ):
        url = url_for(self.endpoint, **url_kwargs)

        if form is None:
            form = {}

        form.update(self.form(client))

        if expected_num_queries is not None:
            with assert_num_queries(expected_num_queries):
                return client.post(url, form=form, headers=headers, follow_redirects=follow_redirects)

        return client.post(url, form=form, headers=headers, follow_redirects=follow_redirects)

    def test_not_logged_in(self, client):
        client_method = getattr(client, self.method)
        response = client_method(self.path, form={"csrf_token": self.fetch_csrf(client)})

        assert response.status_code in (302, 303)
        assert response.location == url_for("backoffice_web.home")

    def test_missing_csrf_token(self, client):
        user = users_factories.UserFactory()

        authenticated_client = client.with_bo_session_auth(user)
        client_method = getattr(authenticated_client, self.method)

        response = client_method(self.path, form={"csrf_token": None})

        assert response.status_code == 400


class PostEndpointHelper(PostEndpointWithoutPermissionHelper, unauthorized.UnauthorizedHelperBase):
    """
    Provides helper method to post with csrf token and checks required permissions
    """

    def test_missing_permission(self, client):
        user = self.setup_user()

        authenticated_client = client.with_bo_session_auth(user)
        client_method = getattr(authenticated_client, self.method)

        response = client_method(self.path, form=self.form(client))
        assert response.status_code == 403

    def test_no_backoffice_profile(self, client):
        user = users_factories.UserFactory()

        authenticated_client = client.with_bo_session_auth(user)
        client_method = getattr(authenticated_client, self.method)

        response = client_method(self.path, form=self.form(client))

        assert response.status_code == 403
