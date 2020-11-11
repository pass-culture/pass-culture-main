import pytest

from pcapi.model_creators.generic_creators import create_user

from tests.conftest import TestClient


RECOMMENDATION_V2_URL = "/recommendations/v2"


class Put:
    class Returns308:
        @pytest.mark.usefixtures("db_session")
        def when_navigating_in_old_recommendations_url(self, app):
            # given
            user = create_user()
            auth_request = TestClient(app.test_client()).with_auth(user.email)

            # when
            response = auth_request.put(RECOMMENDATION_V2_URL, json={})

            # then
            assert response.status_code == 308
            assert response.location == "http://localhost/recommendations"
