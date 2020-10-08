from unittest.mock import patch, MagicMock

import pytest

from pcapi.connectors.api_recaptcha import validate_recaptcha_token, RECAPTCHA_API_URL, ReCaptchaException


@patch('pcapi.connectors.api_recaptcha.RECAPTCHA_SECRET', "recaptcha-secret")
@patch('pcapi.connectors.api_recaptcha.requests.post')
def test_should_return_request_response_from_api(request_post):
    # Given
    expected_response = True
    token = 'my-token'

    response_return_value = MagicMock(status_code=200, text='')
    response_return_value.json = MagicMock(return_value={'success': expected_response})
    request_post.return_value = response_return_value

    # When
    api_response = validate_recaptcha_token(token)

    # Then
    request_post.assert_called_once_with(RECAPTCHA_API_URL,
                                         data={"secret": "recaptcha-secret", "response": token})
    assert api_response == expected_response

@patch('pcapi.connectors.api_recaptcha.RECAPTCHA_SECRET', "recaptcha-secret")
@patch('pcapi.connectors.api_recaptcha.requests.post')
def test_should_raise_exception_when_api_call_fails(request_post):
    # Given
    token = 'test'

    response_return_value = MagicMock(status_code=400, text='')
    request_post.return_value = response_return_value

    # When
    with pytest.raises(ReCaptchaException) as exception:
        validate_recaptcha_token(token)

    # Then
    assert str(exception.value) == "Couldn't reach recaptcha api: 400 "
