import datetime
from unittest.mock import MagicMock
from unittest.mock import patch
import uuid

import pytest

from pcapi.connectors.api_recaptcha import RECAPTCHA_API_URL
from pcapi.connectors.api_recaptcha import ReCaptchaException
from pcapi.connectors.api_recaptcha import validate_recaptcha_token


ORIGINAL_ACTION = "submit"
high_score_return_value = MagicMock(status_code=200, text="")
high_score_return_value.json = MagicMock(
    return_value={
        "success": True,
        "score": 0.5,
        "action": "submit",
        "challenge_ts": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S%Z"),
        "hostname": "url",
    }
)
low_score_return_value = MagicMock(status_code=200, text="")
low_score_return_value.json = MagicMock(
    return_value={
        "success": True,
        "score": 0.4,
        "action": "submit",
        "challenge_ts": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S%Z"),
        "hostname": "url",
    }
)
bad_request_return_value = MagicMock(status_code=400, text="")
invalid_recaptcha_without_specific_error_return_value = MagicMock(status_code=200, text="")
invalid_recaptcha_without_specific_error_return_value.json = MagicMock(
    return_value={
        "success": False,
    }
)
wrong_action_return_value = MagicMock(status_code=200, text="")
wrong_action_return_value.json = MagicMock(
    return_value={
        "success": True,
        "score": 0.9,
        "action": "send",
        "challenge_ts": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S%Z"),
        "hostname": "url",
    }
)
errors_return_value = MagicMock(status_code=200, text="")
errors_return_value.json = MagicMock(
    return_value={
        "success": False,
        "error-codes": ["timeout-or-duplicate", "unknown-error"],
    }
)
test_api_recaptcha_exceptions_data = {
    "bad_request": (bad_request_return_value, "Couldn't reach recaptcha api: 400 "),
    "invalid_request": (invalid_recaptcha_without_specific_error_return_value, "This is not a valid reCAPTCHA token"),
    "wrong_action": (wrong_action_return_value, "The action 'send' does not match 'submit' from the form"),
    "errors": (
        errors_return_value,
        "Encountered the following error(s): ['The response is no longer valid: either is too old or has been used previously.', 'unknown-error']",
    ),
}
test_valid_response_from_api_data = {
    "high_score": (high_score_return_value, True),
    "low_score": (low_score_return_value, False),
}


def generate_fake_token() -> str:
    return str(uuid.uuid4())


@pytest.mark.parametrize(
    "response_return_value,expected_result",
    test_valid_response_from_api_data.values(),
    ids=test_valid_response_from_api_data.keys(),
)
@patch("pcapi.connectors.api_recaptcha.RECAPTCHA_SECRET", "recaptcha-secret")
@patch("pcapi.connectors.api_recaptcha.requests.post")
def test_valid_response_from_api(request_post, response_return_value, expected_result):
    # Given
    token = generate_fake_token()
    request_post.return_value = response_return_value

    # When
    api_response = validate_recaptcha_token(token, ORIGINAL_ACTION)

    # Then
    request_post.assert_called_once_with(RECAPTCHA_API_URL, data={"secret": "recaptcha-secret", "response": token})
    assert api_response == expected_result


@patch("pcapi.connectors.api_recaptcha.requests.post")
def test_with_empty_token(request_post):
    # Given
    request_post.return_value = errors_return_value

    # When
    api_response = validate_recaptcha_token(None, ORIGINAL_ACTION)

    # Then
    request_post.assert_not_called()
    assert api_response is False


@pytest.mark.parametrize(
    "response_return_value,exception_value",
    test_api_recaptcha_exceptions_data.values(),
    ids=test_api_recaptcha_exceptions_data.keys(),
)
@patch("pcapi.connectors.api_recaptcha.RECAPTCHA_SECRET", "recaptcha-secret")
@patch("pcapi.connectors.api_recaptcha.requests.post")
def test_api_recaptcha_exceptions(request_post, response_return_value, exception_value):
    # Given
    token = generate_fake_token()
    request_post.return_value = response_return_value

    # When
    with pytest.raises(ReCaptchaException) as exception:
        validate_recaptcha_token(token, ORIGINAL_ACTION)

    # Then
    assert str(exception.value) == exception_value
