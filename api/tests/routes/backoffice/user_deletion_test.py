import urllib.parse

from flask import url_for
import pytest

from pcapi.core.testing import override_settings
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models

from tests.routes.backoffice.helpers import post as post_endpoint_helper


pytestmark = [pytest.mark.usefixtures("db_session"), pytest.mark.backoffice]


class UserDeletionPostRouteTest(post_endpoint_helper.PostEndpointWithoutPermissionHelper):
    endpoint = "backoffice_web.delete_user"
    needed_permission = None

    def test_sso_user_deletion(self, authenticated_client):
        user = users_factories.UserFactory()
        users_factories.SingleSignOnFactory(user=user)

        response = self.post_to_endpoint(authenticated_client, form={"email": user.email})

        assert response.status_code == 303, response.data
        assert users_models.User.query.filter(users_models.User.id == user.id).one_or_none() is None
        assert urllib.parse.urlparse(response.headers["location"]).path == url_for("backoffice_web.delete_user")

    def test_user_with_relations_deletion_failure(self, authenticated_client):
        user = users_factories.BeneficiaryFactory()

        response = self.post_to_endpoint(authenticated_client, form={"email": user.email})

        assert response.status_code == 303
        assert users_models.User.query.filter(users_models.User.id == user.id).one_or_none() is not None
        assert urllib.parse.urlparse(response.headers["location"]).path == url_for("backoffice_web.delete_user")

    @override_settings(ENABLE_TEST_USER_GENERATION=0)
    def test_user_deletion_disabled(self, authenticated_client):
        user = users_factories.BeneficiaryFactory()

        response = self.post_to_endpoint(authenticated_client, form={"email": user.email})

        assert response.status_code == 404
        assert users_models.User.query.filter(users_models.User.id == user.id).one_or_none() is not None
