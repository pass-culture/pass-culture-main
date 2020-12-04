from unittest.mock import MagicMock
from unittest.mock import patch

from pcapi.connectors.api_recaptcha import RECAPTCHA_API_URL
from pcapi.connectors.api_recaptcha import get_token_validation_and_score


def _build_mocked_request_response(response: dict):
    answer_with_weak_score = MagicMock(status_code=200, text="")
    answer_with_weak_score.json.return_value = response
    return answer_with_weak_score


class GetTokenValidationAndScoreTest:
    @patch("pcapi.connectors.api_recaptcha.RECAPTCHA_SECRET", "recaptcha-secret")
    @patch("pcapi.connectors.api_recaptcha.requests.post")
    def test_should_call_captcha_api_using_secret(self, request_post):
        # Given
        token = "fake-token"
        request_post.return_value = _build_mocked_request_response({"success": True, "score": 0.9, "action": "ACTION"})

        # When
        get_token_validation_and_score(token)

        # Then
        request_post.assert_called_once_with(RECAPTCHA_API_URL, data={"secret": "recaptcha-secret", "response": token})

    @patch("pcapi.connectors.api_recaptcha.RECAPTCHA_SECRET", "recaptcha-secret")
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
