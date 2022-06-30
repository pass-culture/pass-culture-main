from unittest import mock

from flask import url_for
import pytest

from pcapi.core.testing import override_features
from pcapi.core.users import factories as users_factories


pytestmark = pytest.mark.usefixtures("db_session")


class AuthenticationTest:
    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_can_authenticate(self, client):
        # given
        user = users_factories.UserFactory(email="toto@passculture.app")
        with mock.patch("pcapi.core.auth.api.get_google_token_id_info") as token_info_mock, mock.patch(
            "pcapi.core.auth.api.get_groups_from_google_workspace"
        ) as google_groups_mock:
            token_info_mock.return_value = {"email": user.email}
            google_groups_mock.return_value = {"groups": []}

            # when
            response = client.get(
                url_for("backoffice_blueprint.get_auth_token", token="example token"),
            )

        # then
        assert response.status_code == 200
        assert len(response.json["token"].split(".")) == 3

    @override_features(ENABLE_BACKOFFICE_API=True)
    def test_cannot_authenticate_with_a_non_passculture_email(self, client):
        # given
        user = users_factories.UserFactory(email="toto@example.com")

        with mock.patch("pcapi.core.auth.api.get_user_from_google_id") as user_from_google_mock:
            user_from_google_mock.return_value = user

            # when
            response = client.get(
                url_for("backoffice_blueprint.get_auth_token", token="example token"),
            )

        # then
        assert response.status_code == 400
        assert response.json["global"] == "not a passsCulture team account"

    def test_cannot_authenticate_with_an_unknown_email(self, client):
        # given
        with mock.patch("pcapi.core.auth.api.get_google_token_id_info") as token_info_mock:
            token_info_mock.return_value = {"email": "toto@passculture.app"}

            # when
            response = client.get(
                url_for("backoffice_blueprint.get_auth_token", token="example token"),
            )

        # then
        assert response.status_code == 400
        assert response.json["global"] == "not a passsCulture team account"
