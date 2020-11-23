from unittest.mock import patch

import pytest

from pcapi.connectors.google_spreadsheet import MissingGoogleKeyException
from pcapi.connectors.google_spreadsheet import get_credentials


class GetCredentialsTest:
    @patch("pcapi.connectors.google_spreadsheet.os.environ.get")
    @patch("pcapi.connectors.google_spreadsheet.ServiceAccountCredentials")
    def test_calls_service_account_credentials_from_temp_file_created_from_environ_variable_when_exists(
        self, ServiceAccountCredentials, get_environment
    ):
        # Given
        get_environment.return_value = (
            "{'type': 'service_account', 'project_id': 'quickstart-1563873852000', 'private_key_id': '128899911',"
            " 'private_key': '-----BEGIN PRIVATE KEY-----\nMIIBAQDoIMQFqZcXC+iE\nnf7NOhDx5EXgrVVnjUE\nt/engEnp\n"
            "-----END PRIVATE KEY-----\n', 'client_email': 'dashboard@gserviceaccount.com', 'client_id': '123456789',"
            " 'auth_uri': 'oauth2_uri', 'token_uri': 'token_uri', 'auth_provider_x509_cert_url': 'oauth2_cert_url',"
            " 'client_x509_cert_url': 'cert_url'}"
        )

        # When
        get_credentials()

        # Then
        ServiceAccountCredentials.from_json_keyfile_name.assert_called_with(
            "/tmp/data.json", ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        )

    @patch("pcapi.connectors.google_spreadsheet.os.environ.get")
    def test_raises_exception_when_no_environ_variable(self, get_environment):
        # Given
        get_environment.return_value = None

        # When / Then
        with pytest.raises(MissingGoogleKeyException):
            get_credentials()

    @patch("pcapi.connectors.google_spreadsheet.os.environ.get")
    def test_raises_exception_when_empty_environ_variable(self, get_environment):
        # Given
        get_environment.return_value = {}

        # When / Then
        with pytest.raises(MissingGoogleKeyException):
            get_credentials()
