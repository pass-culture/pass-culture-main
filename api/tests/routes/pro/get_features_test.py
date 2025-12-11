import pytest

from pcapi.core import testing
from pcapi.core.users import factories as users_factories
from pcapi.routes.pro import features


class Returns200Test:
    @pytest.mark.usefixtures("db_session")
    def when_user_is_logged_in(self, client):
        user = users_factories.UserFactory()

        queries = testing.AUTHENTICATION_QUERIES
        queries += 1  # select features
        client = client.with_session_auth(user.email)
        with testing.assert_num_queries(queries):
            response = client.get("/features")
            assert response.status_code == 200

        feature_names = {feature_dict["name"] for feature_dict in response.json}
        assert feature_names == {feature.name for feature in features.PRO_FEATURES}
        assert "SYNCHRONIZE_ALLOCINE" not in feature_names

    @pytest.mark.usefixtures("db_session")
    def when_user_is_not_logged_in(self, client):
        queries = 1  # select features
        with testing.assert_num_queries(queries):
            response = client.get("/features")
            assert response.status_code == 200
