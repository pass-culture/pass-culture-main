from unittest.mock import patch

import pytest

from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import ApiErrors

from tests.conftest import TestClient


class Returns200Test:
    @pytest.mark.usefixtures("db_session")
    def when_current_user_changes_password(self, app):
        # given
        user = users_factories.UserFactory(email="user@example.com")
        data = {
            "oldPassword": user.clearTextPassword,
            "newPassword": "N3W_p4ssw0rd",
            "newConfirmationPassword": "N3W_p4ssw0rd",
        }
        user_id = user.id

        # when
        response = TestClient(app.test_client()).with_auth(user.email).post("/users/current/change-password", json=data)

        # then
        user = users_models.User.query.get(user_id)
        assert user.checkPassword("N3W_p4ssw0rd") is True
        assert response.status_code == 204


class Returns400Test:
    @pytest.mark.usefixtures("db_session")
    @patch("pcapi.routes.shared.passwords.validate_change_password_request")
    def when_one_password_is_missing_in_the_request_body(self, validate_change_password_request, app):
        # given
        api_errors = ApiErrors()
        api_errors.add_error("password", "missing password")
        api_errors.status_code = 400
        user = users_factories.UserFactory(email="user@example.com")
        validate_change_password_request.side_effect = api_errors
        data = {}

        # when
        response = TestClient(app.test_client()).with_auth(user.email).post("/users/current/change-password", json=data)

        # then
        assert response.status_code == 400
        assert response.json["password"] == ["missing password"]
