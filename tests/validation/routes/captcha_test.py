from unittest.mock import patch
import uuid

import pytest

from pcapi.validation.routes.captcha import InvalidRecaptchaTokenException
from pcapi.validation.routes.captcha import ReCaptchaException
from pcapi.validation.routes.captcha import check_recaptcha_token_is_valid


ORIGINAL_ACTION = "submit"


def generate_fake_token() -> str:
    return str(uuid.uuid4())


class CheckRecaptchaTokenIsValidTest:
    @patch("pcapi.validation.routes.captcha.IS_RUNNING_TESTS", False)
    @patch("pcapi.validation.routes.captcha.get_token_validation_and_score")
    def test_should_raise_when_score_is_too_low(self, recaptcha_response):
        # Given
        token = generate_fake_token()
        recaptcha_response.return_value = {"success": True, "score": 0.2}

        # When
        with pytest.raises(InvalidRecaptchaTokenException):
            check_recaptcha_token_is_valid(token, ORIGINAL_ACTION, 0.5)

    @patch("pcapi.validation.routes.captcha.IS_RUNNING_TESTS", False)
    @patch("pcapi.validation.routes.captcha.get_token_validation_and_score")
    def test_should_raise_when_action_is_not_matching_the_original_action(self, recaptcha_response):
        # Given
        token = generate_fake_token()
        recaptcha_response.return_value = {"success": True, "score": 0.9, "action": "fake-action"}

        # When
        with pytest.raises(ReCaptchaException) as exception:
            check_recaptcha_token_is_valid(token, ORIGINAL_ACTION, 0.5)

        # Then
        assert str(exception.value) == "The action 'fake-action' does not match 'submit' from the form"

    @patch("pcapi.validation.routes.captcha.IS_RUNNING_TESTS", False)
    @patch("pcapi.validation.routes.captcha.get_token_validation_and_score")
    def test_should_raise_when_token_is_too_old_or_already_used(self, recaptcha_response):
        # Given
        token = generate_fake_token()
        recaptcha_response.return_value = {
            "success": False,
            "error-codes": ["timeout-or-duplicate"],
        }

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
    @patch("pcapi.validation.routes.captcha.IS_RUNNING_TESTS", False)
    @patch("pcapi.validation.routes.captcha.get_token_validation_and_score")
    def test_should_raise_exception_for_any_other_error_code(self, recaptcha_response, error_code):
        # Given
        token = generate_fake_token()
        recaptcha_response.return_value = {
            "success": False,
            "error-codes": [error_code],
        }

        # When
        with pytest.raises(ReCaptchaException):
            check_recaptcha_token_is_valid(token, ORIGINAL_ACTION, 0.5)

    @patch("pcapi.validation.routes.captcha.IS_RUNNING_TESTS", False)
    @patch("pcapi.validation.routes.captcha.get_token_validation_and_score")
    def test_should_raise_exception_with_details(self, recaptcha_response):
        # Given
        token = generate_fake_token()
        recaptcha_response.return_value = {
            "success": False,
            "error-codes": ["first-error", "second-error"],
        }

        # When
        with pytest.raises(ReCaptchaException) as exception:
            check_recaptcha_token_is_valid(token, ORIGINAL_ACTION, 0.5)

        assert str(exception.value) == "Encountered the following error(s): ['first-error', 'second-error']"
