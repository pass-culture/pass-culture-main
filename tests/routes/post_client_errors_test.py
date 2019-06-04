import pytest

from tests.conftest import TestClient
from tests.test_utils import API_URL


@pytest.mark.standalone
class Post:
    class Returns200:
        def when_json_error_is_received(self, app):
            # when
            response = TestClient().post(
                API_URL + '/api/client_errors/store',
                json={'some': {'js': {'errors': ['error1', 'error2']}}},
                headers={
                    'Content-Type': 'text/plain;charset=UTF-8',
                    'Origin': 'http://localhost:3000'
                }
            )

            # then
            assert response.status_code == 200
            assert response.json() == 'Email correctly sent to dev with client error data'

    class Returns400:
        def when_no_json_is_received(self, app):
            # when
            response = TestClient().post(
                API_URL + '/api/client_errors/store'
            )

            # then
            assert response.status_code == 400
            assert response.text == '"Data expected"\n'
