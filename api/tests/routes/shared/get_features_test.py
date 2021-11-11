import pytest

from pcapi.core.users import factories as users_factories

from tests.conftest import TestClient


class Returns200Test:
    @pytest.mark.usefixtures("db_session")
    def when_user_is_logged_in(self, app):
        # given
        user = users_factories.UserFactory()

        # when
        response = TestClient(app.test_client()).with_session_auth(user.email).get("/features")

        # then
        assert response.status_code == 200
        feature_name_keys = [feature_dict["nameKey"] for feature_dict in response.json]
        assert "WEBAPP_SIGNUP" in feature_name_keys

    @pytest.mark.usefixtures("db_session")
    def when_user_is_not_logged_in(self, app):
        # when
        response = TestClient(app.test_client()).get("/features")

        # then
        assert response.status_code == 200
