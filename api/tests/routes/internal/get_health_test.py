from unittest.mock import patch

from tests.conftest import TestClient


class Returns200Test:
    @patch("pcapi.routes.internal.health_check.read_version_from_file")
    def when_api_is_available(self, mock_read_version_from_file, app):
        # Given
        mock_read_version_from_file.return_value = "v69.0.0"

        # When
        response = TestClient(app.test_client()).get("/health/api")

        # Then
        assert response.status_code == 200
        assert str(response.data, "utf-8") == "v69.0.0"

    @patch("pcapi.routes.internal.health_check.read_version_from_file")
    @patch("pcapi.routes.internal.health_check.check_database_connection")
    def when_database_is_available(self, mock_check_database_connection, mock_read_version_from_file, app):
        # Given
        mock_check_database_connection.return_value = True
        mock_read_version_from_file.return_value = "v69.0.0"

        # When
        response = TestClient(app.test_client()).get("/health/database")

        # Then
        assert response.status_code == 200
        assert str(response.data, "utf-8") == "v69.0.0"


class Returns500Test:
    @patch("pcapi.routes.internal.health_check.read_version_from_file")
    @patch("pcapi.routes.internal.health_check.check_database_connection")
    def when_database_is_not_available(self, mock_check_database_connection, mock_read_version_from_file, app):
        # Given
        mock_check_database_connection.return_value = False
        mock_read_version_from_file.return_value = "v69.0.0"

        # when
        response = TestClient(app.test_client()).get("/health/database")

        # then
        assert response.status_code == 500
        assert str(response.data, "utf-8") == "v69.0.0"
