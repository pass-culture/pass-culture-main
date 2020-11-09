import pytest

from pcapi.model_creators.generic_creators import API_URL
from pcapi.model_creators.generic_creators import create_user
from pcapi.repository import repository

from tests.conftest import TestClient


class Get:
    class Returns200:
        @pytest.mark.usefixtures("db_session")
        def when_user_is_logged_in(self, app):
            # given
            user = create_user()
            repository.save(user)

            # when
            response = TestClient(app.test_client()).with_auth(user.email) \
                .get(API_URL + '/features')

            # then
            assert response.status_code == 200
            feature_name_keys = [
                feature_dict['nameKey']
                for feature_dict in response.json
            ]
            assert 'WEBAPP_SIGNUP' in feature_name_keys

        @pytest.mark.usefixtures("db_session")
        def when_user_is_not_logged_in(self, app):
            # when
            response = TestClient(app.test_client()).get(API_URL + '/features')

            # then
            assert response.status_code == 200
