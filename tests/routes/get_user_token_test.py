import pytest

from models import PcObject
from tests.conftest import clean_database, TestClient
from tests.test_utils import API_URL, create_user


@pytest.mark.standalone
class Get:
    class Returns200:
        @clean_database
        def when_activation_token_exists(self, app):
            # given
            token = 'U2NCXTNB2'
            user = create_user(reset_password_token=token)
            PcObject.save(user)

            # when
            request = TestClient().get(API_URL + '/users/token/' + token)

            # then
            assert request.status_code == 200

    class Returns404:
        @clean_database
        def when_activation_token_does_not_exist(self, app):
            # when
            request = TestClient().get(API_URL + '/users/token/3YU26FS')

            # then
            assert request.status_code == 404
