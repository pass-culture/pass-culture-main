import urllib.parse

from flask import url_for
import pytest

from pcapi.core.testing import override_settings
import pcapi.core.users.factories as users_factories
import pcapi.core.users.models as users_models

from tests.routes.backoffice_v3.helpers import html_parser
from tests.routes.backoffice_v3.helpers import post as post_endpoint_helper


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice_v3,
]


class UserGenerationGetRouteTest:
    endpoint = "backoffice_v3_web.get_generated_user"
    needed_permission = None

    def test_returns_user_data(self, authenticated_client):
        generated_user = users_factories.UserFactory()

        response = authenticated_client.get(url_for(self.endpoint, userId=generated_user.id))

        assert response.status_code == 200
        assert generated_user.email in html_parser.content_as_text(response.data)


class UserGenerationPostRouteTest(post_endpoint_helper.PostEndpointWithoutPermissionHelper):
    endpoint = "backoffice_v3_web.generate_user"
    needed_permission = None

    @override_settings(ENABLE_TEST_USER_GENERATION=False)
    def test_returns_not_found_if_generation_disabled(self, authenticated_client):
        form = {"age": "18", "id_provider": "UBBLE", "step": "BENEFICIARY"}
        response = self.post_to_endpoint(authenticated_client, form=form)
        assert response.status_code == 404

    def test_user_not_created_when_18yo_identified_with_educonnect(self, authenticated_client):
        number_of_users_before = users_models.User.query.count()
        form = {"age": "18", "id_provider": "EDUCONNECT", "step": "BENEFICIARY"}
        response = self.post_to_endpoint(authenticated_client, form=form)
        number_of_users_after = users_models.User.query.count()
        assert response.status_code == 303
        assert urllib.parse.urlparse(response.headers["location"]).path == url_for(
            "backoffice_v3_web.get_generated_user"
        )
        assert number_of_users_before == number_of_users_after

    def test_user_not_created_when_underage_validates_phone_number(self, authenticated_client):
        number_of_users_before = users_models.User.query.count()
        form = {"age": "17", "id_provider": "EDUCONNECT", "step": "PHONE_VALIDATION"}
        response = self.post_to_endpoint(authenticated_client, form=form)
        number_of_users_after = users_models.User.query.count()
        assert response.status_code == 303
        assert urllib.parse.urlparse(response.headers["location"]).path == url_for(
            "backoffice_v3_web.get_generated_user"
        )
        assert number_of_users_before == number_of_users_after
