from unittest.mock import patch

from tests.conftest import TestClient


class Get:
    class Returns200:
        @patch('routes.health_check.read_version_from_file', return_value='v69.0.0')
        def when_api_is_available(self, mock_read_version_from_file, app):
            # when
            response = TestClient(app.test_client()).with_auth('test@email.com').get('/health/api')

            # then
            assert response.status_code == 200
            assert response.json == {'version': 'v69.0.0'}

        @patch('routes.health_check.read_version_from_file', return_value='v69.0.0')
        @patch('routes.health_check.check_database_connection', return_value=True)
        def when_database_is_available(self, mock_check_database_connection, mock_read_version_from_file, app):
            # when
            response = TestClient(app.test_client()).with_auth('test@email.com').get('/health/database')

            # then
            assert response.status_code == 200
            assert response.json == {'version': 'v69.0.0'}

    class Returns500:
        @patch('routes.health_check.read_version_from_file', return_value='v69.0.0')
        @patch('routes.health_check.check_database_connection', return_value=False)
        def when_database_is_not_available(self, mock_check_database_connection, mock_read_version_from_file, app):
            # when
            response = TestClient(app.test_client()).with_auth('test@email.com').get('/health/database')

            # then
            assert response.status_code == 500
            assert response.json == {'version': 'v69.0.0'}
