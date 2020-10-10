from pcapi.repository import repository
import pytest
from tests.conftest import TestClient
from pcapi.model_creators.generic_creators import create_user


class Get:
    class Returns200:
        @pytest.mark.usefixtures("db_session")
        def when_activation_token_exists(self, app):
            # given
            token = 'U2NCXTNB2'
            user = create_user(reset_password_token=token)
            repository.save(user)

            # when
            request = TestClient(app.test_client()).get('/users/token/' + token)

            # then
            assert request.status_code == 200
            assert request.json == {}

    class Returns404:
        @pytest.mark.usefixtures("db_session")
        def when_activation_token_does_not_exist(self, app):
            # when
            request = TestClient(app.test_client()).get('/users/token/3YU26FS')

            # then
            assert request.status_code == 404
