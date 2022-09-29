from urllib.parse import parse_qs
from urllib.parse import urlparse

from flask import url_for
import pytest

from pcapi.core.permissions import models as perm_models
from pcapi.core.testing import override_features
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models


pytestmark = pytest.mark.usefixtures("db_session")


@pytest.fixture(scope="function", name="legit_user")
def legit_user_fixture() -> users_models.User:
    user = users_factories.UserFactory(isActive=True)

    permission = perm_models.Permission.query.filter(
        perm_models.Permission.name == perm_models.Permissions.SEARCH_PUBLIC_ACCOUNT.name
    ).first()

    user.backoffice_permissions = [permission]

    return user


class SearchPageTest:
    class UnauthorizedTest:
        @override_features(ENABLE_NEW_BACKOFFICE_POC=True)
        def test_missing_permission(self, client):  # type: ignore
            user = users_factories.UserFactory(isActive=True)
            response = client.with_session_auth(user.email).get(url_for("poc_backoffice_web.search"))

            assert response.status_code == 302
            assert response.location == url_for("poc_backoffice_web.unauthorized", _external=True)

        @override_features(ENABLE_NEW_BACKOFFICE_POC=True)
        def test_not_logged_in(self, client):  # type: ignore
            response = client.get(url_for("poc_backoffice_web.search"))
            assert response.status_code == 302
            assert response.location == url_for("poc_backoffice_web.unauthorized", _external=True)

        @override_features(ENABLE_NEW_BACKOFFICE_POC=False)
        def test_ff_disabled(self, client):  # type: ignore
            response = client.get(url_for("poc_backoffice_web.search"))

            assert response.status_code == 302
            assert response.location == url_for("poc_backoffice_web.unauthorized", _external=True)

    class AuthorizedTest:
        @override_features(ENABLE_NEW_BACKOFFICE_POC=True)
        def test_view_empty_search_page(self, client, legit_user):  # type: ignore
            response = client.with_session_auth(legit_user.email).get(url_for("poc_backoffice_web.search"))
            assert response.status_code == 200

        @override_features(ENABLE_NEW_BACKOFFICE_POC=True)
        def test_search_result_page(self, client, legit_user):  # type: ignore
            url = url_for("poc_backoffice_web.search", query=legit_user.email, order_by="", page=1, per_page=20)

            response = client.with_session_auth(legit_user.email).get(url)
            assert legit_user.email in str(response.data)
            assert response.status_code == 200

        @override_features(ENABLE_NEW_BACKOFFICE_POC=True)
        def test_send_search_form(self, client, legit_user):  # type: ignore
            dst = url_for("poc_backoffice_web.search")
            form_data = {"query": "Jean", "order_by": "", "page": 1, "per_page": 20}

            response = client.with_session_auth(legit_user.email).post(dst, form=form_data)

            assert response.status_code == 302

            parsed_location = urlparse(response.location)
            assert parsed_location.path == url_for("poc_backoffice_web.search")

            assert parse_qs(parsed_location.query) == {
                "query": ["Jean"],
                "page": ["1"],
                "per_page": ["20"],
            }
