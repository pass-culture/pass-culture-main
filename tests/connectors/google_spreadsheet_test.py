from os import path
from pathlib import Path
from unittest.mock import patch, MagicMock

from connectors.google_spreadsheet import get_credentials


class GetCredentialsTest:
    @patch('connectors.google_spreadsheet.os.environ.get')
    @patch('connectors.google_spreadsheet.ServiceAccountCredentials')
    def test_calls_service_account_credentials_from_temp_file_created_from_environ_variable_when_exists(self,
                                                                                                        ServiceAccountCredentials,
                                                                                                        get_environment):
        # Given
        get_environment.return_value = '{"type": "service_account", ' \
                                       '"project_id": "pass-culture", "private_key_id": "1234",  ' \
                                       '"private_key": "-----BEGIN PRIVATE KEY-----12345' \
                                       '-----END PRIVATE KEY-----", ' \
                                       '"client_email": "client@email.com", ' \
                                       '"client_id": "4321", ' \
                                       '"auth_uri": "https://url.com", ' \
                                       '"token_uri": "https://url.com/token", ' \
                                       '"auth_provider_x509_cert_url": "https://url.com/certs", ' \
                                       '"client_x509_cert_url": "https://url.com/client_x509_cert_url"}'

        # When
        get_credentials()

        # Then
        ServiceAccountCredentials.from_json_keyfile_name.assert_called_with('/tmp/data.json',
                                                                            ['https://spreadsheets.google.com/feeds',
                                                                             'https://www.googleapis.com/auth/drive'])

    @patch('connectors.google_spreadsheet.os.environ.get')
    @patch('connectors.google_spreadsheet.ServiceAccountCredentials')
    def test_calls_service_account_credentials_from_private_file_when_no_environ_variable(self,
                                                                             ServiceAccountCredentials,
                                                                             get_environment):
        # Given
        get_environment.return_value = None
        expected_google_key_path = Path('/opt/services/flaskapp/src/connectors/../private/google_key.json')

        # When
        get_credentials()

        # Then
        ServiceAccountCredentials.from_json_keyfile_name.assert_called_with(expected_google_key_path,
                                                                            ['https://spreadsheets.google.com/feeds',
                                                                             'https://www.googleapis.com/auth/drive'])

    @patch('connectors.google_spreadsheet.os.environ.get')
    @patch('connectors.google_spreadsheet.ServiceAccountCredentials')
    def test_calls_service_account_credentials_from_private_file_when_empty_environ_variable(self,
                                                                             ServiceAccountCredentials,
                                                                             get_environment):
        # Given
        get_environment.return_value = {}
        expected_google_key_path = Path('/opt/services/flaskapp/src/connectors/../private/google_key.json')

        # When
        get_credentials()

        # Then
        ServiceAccountCredentials.from_json_keyfile_name.assert_called_with(expected_google_key_path,
                                                                            ['https://spreadsheets.google.com/feeds',
                                                                             'https://www.googleapis.com/auth/drive'])
