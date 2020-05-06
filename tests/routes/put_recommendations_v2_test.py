from tests.conftest import clean_database, TestClient
from tests.model_creators.generic_creators import create_user


RECOMMENDATION_V2_URL = '/recommendations/v2'


class Put:
    class Returns308:
        @clean_database
        def when_navigating_in_old_recommendations_url(self, app):
            # given
            user = create_user()
            auth_request = TestClient(app.test_client()).with_auth(user.email)

            # when
            response = auth_request.put(RECOMMENDATION_V2_URL,
                                        json={})

            # then
            assert response.status_code == 308
            assert response.location == 'http://localhost/recommendations'
