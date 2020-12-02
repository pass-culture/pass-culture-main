from unittest.mock import MagicMock
from unittest.mock import patch
import uuid

import pytest

from pcapi.connectors.api_recaptcha import RECAPTCHA_API_URL
from pcapi.connectors.api_recaptcha import InvalidRecaptchaTokenException
from pcapi.connectors.api_recaptcha import ReCaptchaException
from pcapi.connectors.api_recaptcha import check_recaptcha_token_is_valid


ORIGINAL_ACTION = "submit"


def generate_fake_token() -> str:
    return str(uuid.uuid4())


def _build_mocked_request_response(response: dict):
    answer_with_weak_score = MagicMock(status_code=200, text="")
    answer_with_weak_score.json = MagicMock(return_value=response)
    return answer_with_weak_score


class CheckRecaptchaTokenIsValidTest:
    @patch("pcapi.connectors.api_recaptcha.RECAPTCHA_SECRET", "recaptcha-secret")
    @patch("pcapi.connectors.api_recaptcha.requests.post")
    def test_should_call_captcha_api_using_secret(self, request_post):
        # Given
        token = generate_fake_token()
        request_post.return_value = _build_mocked_request_response(
            {"success": True, "score": 0.9, "action": ORIGINAL_ACTION}
        )

        # When
        check_recaptcha_token_is_valid(token, ORIGINAL_ACTION, 0.5)

        # Then
        request_post.assert_called_once_with(RECAPTCHA_API_URL, data={"secret": "recaptcha-secret", "response": token})

    @patch("pcapi.connectors.api_recaptcha.RECAPTCHA_SECRET", "recaptcha-secret")
    @patch("pcapi.connectors.api_recaptcha.requests.post")
    def test_should_raise_when_score_is_too_low(self, request_post):
        # Given
        token = generate_fake_token()
        request_post.return_value = _build_mocked_request_response({"success": True, "score": 0.2})

        # When
        with pytest.raises(ReCaptchaException) as exception:
            check_recaptcha_token_is_valid(token, ORIGINAL_ACTION, 0.5)

        # Then
        assert str(exception.value) == "Token score is too low (0.2) to match minimum score (0.5)"

    @patch("pcapi.connectors.api_recaptcha.RECAPTCHA_SECRET", "recaptcha-secret")
    @patch("pcapi.connectors.api_recaptcha.requests.post")
    def test_should_raise_when_action_is_not_matching_the_original_action(self, request_post):
        # Given
        token = generate_fake_token()
        request_post.return_value = _build_mocked_request_response(
            {"success": True, "score": 0.9, "action": "fake-action"}
        )

        # When
        with pytest.raises(ReCaptchaException) as exception:
            check_recaptcha_token_is_valid(token, ORIGINAL_ACTION, 0.5)

        # Then
        assert str(exception.value) == "The action 'fake-action' does not match 'submit' from the form"

    @patch("pcapi.connectors.api_recaptcha.RECAPTCHA_SECRET", "recaptcha-secret")
    @patch("pcapi.connectors.api_recaptcha.requests.post")
    def test_should_raise_when_token_is_too_old_or_already_used(self, request_post):
        # Given
        token = generate_fake_token()
        request_post.return_value = _build_mocked_request_response(
            {
                "success": False,
                "error-codes": ["timeout-or-duplicate"],
            }
        )

        # When
        with pytest.raises(InvalidRecaptchaTokenException):
            check_recaptcha_token_is_valid(token, ORIGINAL_ACTION, 0.5)

    @pytest.mark.parametrize(
        "error_code",
        [
            "missing-input-secret",
            "invalid-input-secret",
            "missing-input-response",
            "invalid-input-response",
            "bad-request",
        ],
    )
    @patch("pcapi.connectors.api_recaptcha.RECAPTCHA_SECRET", "recaptcha-secret")
    @patch("pcapi.connectors.api_recaptcha.requests.post")
    def test_should_raise_exception_for_any_other_error_code(self, request_post, error_code):
        # Given
        token = generate_fake_token()
        request_post.return_value = _build_mocked_request_response(
            {
                "success": False,
                "error-codes": [error_code],
            }
        )

        # When
        with pytest.raises(ReCaptchaException):
            check_recaptcha_token_is_valid(token, ORIGINAL_ACTION, 0.5)

    @patch("pcapi.connectors.api_recaptcha.RECAPTCHA_SECRET", "recaptcha-secret")
    @patch("pcapi.connectors.api_recaptcha.requests.post")
    def test_should_raise_exception_with_details(self, request_post):
        # Given
        token = generate_fake_token()
        request_post.return_value = _build_mocked_request_response(
            {
                "success": False,
                "error-codes": ["first-error", "second-error"],
            }
        )

        # When
        with pytest.raises(ReCaptchaException) as exception:
            check_recaptcha_token_is_valid(token, ORIGINAL_ACTION, 0.5)

        assert str(exception.value) == "Encountered the following error(s): ['first-error', 'second-error']"
