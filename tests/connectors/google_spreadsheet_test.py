import json
from unittest.mock import patch

import pytest

from pcapi.connectors.google_spreadsheet import MissingGoogleKeyException
from pcapi.connectors.google_spreadsheet import get_credentials


class GetCredentialsTest:
    @patch("pcapi.connectors.google_spreadsheet.os.environ.get")
    @patch("google.oauth2.service_account.Credentials.from_service_account_info")
    def test_calls_from_service_account_info(
        self,
        from_service_account_info,
        get_environment,
    ):
        # Given
        account_info_as_json = (
            "{"
            '"type": "service_account",'
            '"project_id": "pass-culture",'
            '"client_email": "a@example.com",'
            '"client_id": "1",'
            '"token_uri": "https://www.example.com/",'
            '"private_key": "the\nprivate\nkey\nwith\nmultiple\nlines"'
            "}"
        )
        # FIXME(cgaunet, 2020-11-24): see `get_credentials` as for why we replace double quotes.
        get_environment.return_value = account_info_as_json.replace('"', "'")

        # When
        get_credentials()

        # Then
        expected_account_info = {
            "type": "service_account",
            "project_id": "pass-culture",
            "client_email": "a@example.com",
            "client_id": "1",
            "token_uri": "https://www.example.com/",
            "private_key": "the\nprivate\nkey\nwith\nmultiple\nlines",
        }
        assert from_service_account_info.call_args[0][0] == expected_account_info
        expected_scopes = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        assert from_service_account_info.call_args[1] == {"scopes": expected_scopes}

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
