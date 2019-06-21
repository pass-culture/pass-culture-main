import pytest

from models import PcObject
from tests.conftest import clean_database, TestClient
from tests.test_utils import API_URL, create_user


@pytest.mark.standalone
class Get:
    class Returns200:
        @clean_database
        def when_user_is_logged_in(self, app):
            # given
            user = create_user()
            PcObject.save(user)

            # when
            response = TestClient().with_auth(user.email) \
                .get(API_URL + '/features')

            # then
            assert response.status_code == 200
            assert response.json() == [
                {'modelName': 'Feature', 'name': 'webapp_signup', 'isActive': True},
            ]

    class Returns401:
        @clean_database
        def when_user_is_not_logged_in(self, app):
            # when
            response = TestClient().get(API_URL + '/features')

            # then
            assert response.status_code == 401
