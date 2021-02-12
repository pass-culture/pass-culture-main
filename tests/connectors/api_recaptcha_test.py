from unittest.mock import MagicMock
from unittest.mock import patch
import uuid

import pytest

from pcapi import settings
from pcapi.connectors.api_recaptcha import InvalidRecaptchaTokenException
from pcapi.connectors.api_recaptcha import ReCaptchaException
from pcapi.connectors.api_recaptcha import check_recaptcha_token_is_valid
from pcapi.connectors.api_recaptcha import get_token_validation_and_score


ORIGINAL_ACTION = "submit"


def _build_mocked_request_response(response: dict):
    answer_with_weak_score = MagicMock(status_code=200, text="")
    answer_with_weak_score.json.return_value = response
    return answer_with_weak_score


def generate_fake_token() -> str:
    return str(uuid.uuid4())


class GetTokenValidationAndScoreTest:
    @patch("pcapi.settings.RECAPTCHA_SECRET", "recaptcha-secret")
    @patch("pcapi.connectors.api_recaptcha.requests.post")
    def test_should_call_captcha_api_using_secret(self, request_post):
        # Given
        token = "fake-token"
        request_post.return_value = _build_mocked_request_response({"success": True, "score": 0.9, "action": "ACTION"})

        # When
        get_token_validation_and_score(token)

        # Then
        request_post.assert_called_once_with(
            settings.RECAPTCHA_API_URL, data={"secret": "recaptcha-secret", "response": token}
        )

    @patch("pcapi.settings.RECAPTCHA_SECRET", "recaptcha-secret")
    @patch("pcapi.connectors.api_recaptcha.requests.post")
    def test_should_return_validation_fields(self, request_post):
        # Given
        token = "fake-token"
        request_post.return_value = _build_mocked_request_response(
            {"success": True, "score": 0.9, "action": "ACTION", "challenge_ts": "", "hostname": "", "error-codes": []}
        )

        # When
        result = get_token_validation_and_score(token)

        # Then
        assert result == {"score": 0.9, "success": True, "action": "ACTION", "error-codes": []}


class CheckRecaptchaTokenIsValidTest:
    @patch("pcapi.connectors.api_recaptcha.settings")
    @patch("pcapi.connectors.api_recaptcha.get_token_validation_and_score")
    def test_should_raise_when_score_is_too_low(self, recaptcha_response, settings_mock):
        # Given
        token = generate_fake_token()
        recaptcha_response.return_value = {"success": True, "score": 0.2}
        settings_mock.IS_DEV = False

        # When
        with pytest.raises(InvalidRecaptchaTokenException):
            check_recaptcha_token_is_valid(token, ORIGINAL_ACTION, 0.5)

    @patch("pcapi.connectors.api_recaptcha.settings")
    @patch("pcapi.connectors.api_recaptcha.get_token_validation_and_score")
    def test_should_raise_when_action_is_not_matching_the_original_action(self, recaptcha_response, settings_mock):
        # Given
        token = generate_fake_token()
        recaptcha_response.return_value = {"success": True, "score": 0.9, "action": "fake-action"}
        settings_mock.IS_DEV = False

        # When
        with pytest.raises(ReCaptchaException) as exception:
            check_recaptcha_token_is_valid(token, ORIGINAL_ACTION, 0.5)

        # Then
        assert str(exception.value) == "The action 'fake-action' does not match 'submit' from the form"

    @patch("pcapi.connectors.api_recaptcha.settings")
    @patch("pcapi.connectors.api_recaptcha.get_token_validation_and_score")
    def test_should_raise_when_token_is_too_old_or_already_used(self, recaptcha_response, settings_mock):
        # Given
        token = generate_fake_token()
        recaptcha_response.return_value = {
            "success": False,
            "error-codes": ["timeout-or-duplicate"],
        }
        settings_mock.IS_DEV = False

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
    @patch("pcapi.connectors.api_recaptcha.settings")
    @patch("pcapi.connectors.api_recaptcha.get_token_validation_and_score")
    def test_should_raise_exception_for_any_other_error_code(self, recaptcha_response, settings_mock, error_code):
        # Given
        token = generate_fake_token()
        recaptcha_response.return_value = {
            "success": False,
            "error-codes": [error_code],
        }
        settings_mock.IS_DEV = False

        # When
        with pytest.raises(ReCaptchaException):
            check_recaptcha_token_is_valid(token, ORIGINAL_ACTION, 0.5)

    @patch("pcapi.connectors.api_recaptcha.settings")
    @patch("pcapi.connectors.api_recaptcha.get_token_validation_and_score")
    def test_should_raise_exception_with_details(self, recaptcha_response, settings_mock):
        # Given
        token = generate_fake_token()
        recaptcha_response.return_value = {
            "success": False,
            "error-codes": ["first-error", "second-error"],
        }
        settings_mock.IS_DEV = False

        # When
        with pytest.raises(ReCaptchaException) as exception:
            check_recaptcha_token_is_valid(token, ORIGINAL_ACTION, 0.5)

        assert str(exception.value) == "Encountered the following error(s): ['first-error', 'second-error']"
