import pytest

from pcapi.core import testing
from pcapi.core.users import factories as users_factories


class Returns200Test:
    @pytest.mark.usefixtures("db_session")
    def when_user_is_logged_in(self, client):
        user = users_factories.UserFactory()

        queries = testing.AUTHENTICATION_QUERIES
        queries += 1  # select features
        client = client.with_session_auth(user.email)
        with testing.assert_num_queries(queries):
            response = client.get("/pro/features")
            assert response.status_code == 200

        feature_name_keys = [feature_dict["nameKey"] for feature_dict in response.json]
        assert "SYNCHRONIZE_ALLOCINE" in feature_name_keys

    @pytest.mark.usefixtures("db_session")
    def when_user_is_not_logged_in(self, client):
        queries = 1  # select features
        with testing.assert_num_queries(queries):
            response = client.get("/pro/features")
            assert response.status_code == 200
