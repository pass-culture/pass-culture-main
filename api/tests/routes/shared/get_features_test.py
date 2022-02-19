import pytest

from pcapi.core.users import factories as users_factories


class Returns200Test:
    @pytest.mark.usefixtures("db_session")
    def when_user_is_logged_in(self, client):
        # given
        user = users_factories.UserFactory()

        # when
        response = client.with_session_auth(user.email).get("/features")

        # then
        assert response.status_code == 200
        feature_name_keys = [feature_dict["nameKey"] for feature_dict in response.json]
        assert "SYNCHRONIZE_ALLOCINE" in feature_name_keys

    @pytest.mark.usefixtures("db_session")
    def when_user_is_not_logged_in(self, client):
        # when
        response = client.get("/features")

        # then
        assert response.status_code == 200
