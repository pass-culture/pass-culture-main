from unittest.mock import patch, MagicMock

import pytest

from connectors.scalingo_api import _get_application_bearer_token, ScalingoApiException, \
    run_process_in_one_off_container


class GetApplicationBearerTokenTest:
    @patch.dict('os.environ', {"SCALINGO_APP_TOKEN": 'token123'})
    @patch('connectors.scalingo_api.requests.post')
    def test_should_call_scalingo_auth_url_with_application_token(self, mock_post):
        # Given
        response_return_value = MagicMock(status_code=200, text='')
        response_return_value.json = MagicMock(return_value={'token': 'bearer_token'})
        mock_post.return_value = response_return_value

        # When
        application_bearer_token = _get_application_bearer_token()

        # Then
        mock_post.assert_called_once_with('https://auth.scalingo.com/v1/tokens/exchange',
                                          auth=(None, "token123"))
        assert application_bearer_token == 'bearer_token'

    @patch('connectors.scalingo_api.requests.post')
    def test_should_raise_exception_when_no_application_token_given(self, mock_post):
        # Given
        response_return_value = MagicMock(status_code=400, text='')
        response_return_value.json = MagicMock(return_value={'error': 'error in application token'})
        mock_post.return_value = response_return_value

        # When
        with pytest.raises(ScalingoApiException) as exception:
            _get_application_bearer_token()

        # Then
        assert str(exception.value) == "Error getting bearer token with status 400:" \
                                       " {'error': 'error in application token'}"


class RunProcessInOneOffContainerTest:
    @patch.dict('os.environ', {"SCALINGO_APP_TOKEN": 'token123'})
    @patch('connectors.scalingo_api.API_APPLICATION_NAME', 'pass-culture-api-app')
    @patch('connectors.scalingo_api.requests.post')
    @patch('connectors.scalingo_api._get_application_bearer_token')
    def test_should_call_scalingo_api_with_expected_payload(self, mock_get_app_token, mock_post):
        # Given
        mock_get_app_token.return_value = 'bearer_token123'
        response_return_value = MagicMock(status_code=200, text='')
        response_return_value.json = MagicMock(return_value={'container': {'id': '12345678987654ERTY'}})
        mock_post.return_value = response_return_value

        # When
        container_id = run_process_in_one_off_container('command_line')

        # Then
        mock_get_app_token.assert_called_once()
        mock_post.assert_called_once_with('https://api.osc-fr1.scalingo.com/v1/apps/pass-culture-api-app/run',
                                          json={"command": 'command_line',
                                                "region": "osc-fr1",
                                                "detached": True,
                                                "size": "L"},
                                          headers={'Authorization': 'Bearer bearer_token123'})
        assert container_id == '12345678987654ERTY'

    @patch.dict('os.environ', {"SCALINGO_APP_TOKEN": 'token123'})
    @patch('connectors.scalingo_api.API_APPLICATION_NAME', 'pass-culture-api-app')
    @patch('connectors.scalingo_api.requests.post')
    @patch('connectors.scalingo_api._get_application_bearer_token')
    def test_should_raise_errors_when_error_during_api_call(self, mock_get_app_token, mock_post):
        # Given
        response_return_value = MagicMock(status_code=400, text='')
        response_return_value.json = MagicMock(return_value={'error': 'error in run app'})
        mock_post.return_value = response_return_value

        # When
        with pytest.raises(ScalingoApiException) as exception:
            run_process_in_one_off_container('command_line')

        # Then
        assert str(exception.value) == "Error getting bearer token with status 400: {'error': 'error in run app'}"
