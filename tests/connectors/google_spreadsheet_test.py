from unittest.mock import patch

import pytest

from pcapi.connectors.google_spreadsheet import MissingGoogleKeyException
from pcapi.connectors.google_spreadsheet import get_credentials


class GetCredentialsTest:
    @patch(
        "pcapi.settings.GOOGLE_KEY",
        (
            "{'type': 'service_account','project_id': 'pass-culture', 'client_email': 'a@example.com', "
            "'client_id': '1', 'token_uri': 'https://www.example.com/', "
            "'private_key': 'the\nprivate\nkey\nwith\nmultiple\nlines'}"
        ),
    )
    @patch("google.oauth2.service_account.Credentials.from_service_account_info")
    def test_calls_from_service_account_info(
        self,
        from_service_account_info,
    ):
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

    @patch("pcapi.settings.GOOGLE_KEY", None)
    def test_raises_exception_when_no_environ_variable(self):
        with pytest.raises(MissingGoogleKeyException):
            get_credentials()

    @patch("pcapi.settings.GOOGLE_KEY", "")
    def test_raises_exception_when_empty_environ_variable(self):
        with pytest.raises(MissingGoogleKeyException):
            get_credentials()
