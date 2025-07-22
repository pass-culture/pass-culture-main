import urllib.parse

import pytest
from flask import url_for

from pcapi import settings
from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import db

from tests.routes.backoffice.helpers import html_parser
from tests.routes.backoffice.helpers import post as post_endpoint_helper
from tests.routes.backoffice.helpers.get import GetEndpointWithoutPermissionHelper


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice,
]


class UserGenerationGetRouteTest(GetEndpointWithoutPermissionHelper):
    endpoint = "backoffice_web.dev.get_generated_user"
    needed_permission = None

    def test_returns_user_data(self, authenticated_client):
        generated_user = users_factories.BaseUserFactory()

        response = authenticated_client.get(url_for(self.endpoint, userId=generated_user.id))

        assert response.status_code == 200
        assert generated_user.email in html_parser.content_as_text(response.data)

    def test_contains_link_to_app_if_token_and_names(self, authenticated_client):
        generated_user = users_factories.ProfileCompletedUserFactory()
        response = authenticated_client.get(
            url_for(
                self.endpoint,
                userId=generated_user.id,
                accessToken="0",
                email=generated_user.email,
                expirationTimestamp=123,
            )
        )

        assert response.status_code == 200
        assert (
            f"Aller sur l'app en tant que {generated_user.firstName} {generated_user.lastName}"
            in html_parser.content_as_text(response.data)
        )

    def test_contains_link_to_app_if_token_and_no_names(self, authenticated_client):
        generated_user = users_factories.BaseUserFactory()
        response = authenticated_client.get(
            url_for(
                self.endpoint,
                userId=generated_user.id,
                accessToken="0",
                email=generated_user.email,
                expirationTimestamp=123,
            )
        )

        assert response.status_code == 200
        assert f"Aller sur l'app en tant que User {generated_user.id}" in html_parser.content_as_text(response.data)

    def test_does_not_contain_link_to_app_if_no_token(self, authenticated_client):
        generated_user = users_factories.ProfileCompletedUserFactory()
        response = authenticated_client.get(url_for(self.endpoint, userId=generated_user.id, accessToken=""))

        assert response.status_code == 200
        assert "Aller sur l'app" not in html_parser.content_as_text(response.data)

    @pytest.mark.settings(UBBLE_MOCK_CONFIG_URL=None)
    def test_does_not_contain_link_to_ubble_mock_if_not_url(self, authenticated_client):
        generated_user = users_factories.BaseUserFactory()

        response = authenticated_client.get(url_for(self.endpoint, userId=generated_user.id))

        assert response.status_code == 200
        assert "Configuration du mock Ubble pour l'utilisateur" not in html_parser.content_as_text(response.data)

    @pytest.mark.settings(UBBLE_MOCK_CONFIG_URL="http://mock-ubble.team")
    def test_does_not_contain_link_to_ubble_mock_if_url_and_not_user(self, authenticated_client):
        response = authenticated_client.get(url_for(self.endpoint, userId=999999999))

        assert response.status_code == 200
        assert "Configuration du mock Ubble pour l'utilisateur" not in html_parser.content_as_text(response.data)

    @pytest.mark.settings(UBBLE_MOCK_CONFIG_URL="http://mock-ubble.team/")
    def test_contains_link_to_ubble_mock_if_url_and_user_id(self, authenticated_client):
        generated_user = users_factories.BaseUserFactory()
        link_to_ubble_mock = (
            settings.UBBLE_MOCK_CONFIG_URL + f"?{urllib.parse.urlencode({'userId': generated_user.id})}"
        )

        response = authenticated_client.get(url_for(self.endpoint, userId=generated_user.id))

        assert response.status_code == 200
        assert link_to_ubble_mock in str(response.data)
        assert "Configuration du mock Ubble pour l'utilisateur" in html_parser.content_as_text(response.data)


class UserGenerationPostRouteTest(post_endpoint_helper.PostEndpointWithoutPermissionHelper):
    endpoint = "backoffice_web.dev.generate_user"
    needed_permission = None

    @pytest.mark.settings(ENABLE_TEST_USER_GENERATION=False)
    def test_returns_not_found_if_generation_disabled(self, authenticated_client):
        form = {"age": "18", "id_provider": "UBBLE", "step": "BENEFICIARY"}
        response = self.post_to_endpoint(authenticated_client, form=form)
        assert response.status_code == 404

    def test_user_not_created_when_18yo_identified_with_educonnect(self, authenticated_client):
        number_of_users_before = db.session.query(users_models.User).count()
        form = {"age": "18", "id_provider": "EDUCONNECT", "step": "BENEFICIARY"}
        response = self.post_to_endpoint(authenticated_client, form=form)
        number_of_users_after = db.session.query(users_models.User).count()
        assert response.status_code == 303
        assert urllib.parse.urlparse(response.headers["location"]).path == url_for(
            "backoffice_web.dev.get_generated_user"
        )
        assert number_of_users_before == number_of_users_after

    def test_user_not_created_when_underage_validates_phone_number(self, authenticated_client):
        number_of_users_before = db.session.query(users_models.User).count()
        form = {"age": "17", "id_provider": "EDUCONNECT", "step": "PHONE_VALIDATION"}
        response = self.post_to_endpoint(authenticated_client, form=form)
        number_of_users_after = db.session.query(users_models.User).count()
        assert response.status_code == 303
        assert urllib.parse.urlparse(response.headers["location"]).path == url_for(
            "backoffice_web.dev.get_generated_user"
        )
        assert number_of_users_before == number_of_users_after

    def test_user_not_created_when_age_below_valid_range(self, authenticated_client):
        number_of_users_before = db.session.query(users_models.User).count()
        form = {"age": "14", "id_provider": "EDUCONNECT", "step": "EMAIL_VALIDATION"}
        response = self.post_to_endpoint(authenticated_client, form=form)
        number_of_users_after = db.session.query(users_models.User).count()
        assert response.status_code == 303
        assert urllib.parse.urlparse(response.headers["location"]).path == url_for(
            "backoffice_web.dev.get_generated_user"
        )
        assert number_of_users_before == number_of_users_after

    def test_user_not_created_when_age_above_valid_range(self, authenticated_client):
        number_of_users_before = db.session.query(users_models.User).count()
        form = {"age": "21", "id_provider": "UBBLE", "step": "EMAIL_VALIDATION"}
        response = self.post_to_endpoint(authenticated_client, form=form)
        number_of_users_after = db.session.query(users_models.User).count()
        assert response.status_code == 303
        assert urllib.parse.urlparse(response.headers["location"]).path == url_for(
            "backoffice_web.dev.get_generated_user"
        )
        assert number_of_users_before == number_of_users_after


class UserDeletionPostRouteTest(post_endpoint_helper.PostEndpointWithoutPermissionHelper):
    endpoint = "backoffice_web.dev.delete_user"
    needed_permission = None

    def test_sso_user_deletion(self, authenticated_client):
        user = users_factories.UserFactory()
        users_factories.SingleSignOnFactory(user=user)
        users_factories.TrustedDeviceFactory(user=user)

        response = self.post_to_endpoint(authenticated_client, form={"email": user.email})

        assert response.status_code == 303, response.data
        assert db.session.query(users_models.User).filter(users_models.User.id == user.id).one_or_none() is None
        assert urllib.parse.urlparse(response.headers["location"]).path == url_for("backoffice_web.dev.delete_user")

    def test_user_with_relations_deletion_failure(self, authenticated_client):
        user = users_factories.BeneficiaryFactory()

        response = self.post_to_endpoint(authenticated_client, form={"email": user.email})

        assert response.status_code == 303
        assert db.session.query(users_models.User).filter(users_models.User.id == user.id).one_or_none() is not None
        assert urllib.parse.urlparse(response.headers["location"]).path == url_for("backoffice_web.dev.delete_user")

    @pytest.mark.settings(ENABLE_TEST_USER_GENERATION=0)
    def test_user_deletion_disabled(self, authenticated_client):
        user = users_factories.BeneficiaryFactory()

        response = self.post_to_endpoint(authenticated_client, form={"email": user.email})

        assert response.status_code == 404
        assert db.session.query(users_models.User).filter(users_models.User.id == user.id).one_or_none() is not None


class ComponentsTest(GetEndpointWithoutPermissionHelper):
    endpoint = "backoffice_web.dev.components"
    needed_permission = None

    @pytest.mark.settings(ENABLE_BO_COMPONENT_PAGE=1)
    def test_returns_user_data(self, authenticated_client):
        response = authenticated_client.get(url_for(self.endpoint))
        assert response.status_code == 200

    @pytest.mark.settings(ENABLE_BO_COMPONENT_PAGE=0)
    def test_returns_user_data_without_bo_component_page(self, authenticated_client):
        response = authenticated_client.get(url_for(self.endpoint))
        assert response.status_code == 404
