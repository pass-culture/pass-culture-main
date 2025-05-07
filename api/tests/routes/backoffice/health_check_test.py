from unittest.mock import patch

import pytest


pytestmark = [
    pytest.mark.usefixtures("db_session"),
    pytest.mark.backoffice,
]


class Returns200Test:
    @patch("pcapi.routes.backoffice.health_check.read_version_from_file")
    def when_api_is_available(self, mock_read_version_from_file, client):
        mock_read_version_from_file.return_value = "v69.0.0"

        response = client.get("/health/api")

        assert response.status_code == 200
        assert str(response.data, "utf-8") == "v69.0.0"

    @patch("pcapi.routes.backoffice.health_check.read_version_from_file")
    @patch("pcapi.routes.backoffice.health_check.check_database_connection")
    def when_database_is_available(self, mock_check_database_connection, mock_read_version_from_file, client):
        mock_check_database_connection.return_value = True
        mock_read_version_from_file.return_value = "v69.0.0"

        response = client.get("/health/database")

        assert response.status_code == 200
        assert str(response.data, "utf-8") == "v69.0.0"


class Returns500Test:
    @patch("pcapi.routes.backoffice.health_check.read_version_from_file")
    @patch("pcapi.routes.backoffice.health_check.check_database_connection")
    def when_database_is_not_available(self, mock_check_database_connection, mock_read_version_from_file, client):
        mock_check_database_connection.return_value = False
        mock_read_version_from_file.return_value = "v69.0.0"

        response = client.get("/health/database")

        assert response.status_code == 500
        assert str(response.data, "utf-8") == "v69.0.0"
