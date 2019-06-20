from tests.conftest import TestClient


class Post:
    class Returns200:
        def when_json_error_is_received(self, app):
            # when
            response = TestClient(app.test_client()).post(
                '/api/client_errors/store',
                json={'some': {'js': {'errors': ['error1', 'error2']}}},
                headers={
                    'Content-Type': 'text/plain;charset=UTF-8',
                    'Origin': 'http://localhost:3000'
                }
            )

            # then
            assert response.status_code == 200
            assert response.json == 'Email correctly sent to dev with client error data'

    class Returns400:
        def when_no_json_is_received(self, app):
            # when
            response = TestClient(app.test_client()).post(
                '/api/client_errors/store',
                json={},
                headers={
                    'Content-Type': 'text/plain;charset=UTF-8',
                    'Origin': 'http://localhost:3000'
                }
            )

            # then
            assert response.status_code == 400
            assert response.data.decode('utf-8') == '"Data expected"\n'
