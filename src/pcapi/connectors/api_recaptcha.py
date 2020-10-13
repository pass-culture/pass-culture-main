import os
import requests


RECAPTCHA_API_URL = 'https://www.google.com/recaptcha/api/siteverify'
RECAPTCHA_SECRET = os.environ.get("RECAPTCHA_SECRET")
RECAPTCHA_REQUIRED_SCORE = os.environ.get("RECAPTCHA_REQUIRED_SCORE", 0.5)
RECAPTCHA_ERROR_CODES = {
    'missing-input-secret': 'The secret parameter is missing.',
    'invalid-input-secret': 'The secret parameter is invalid or malformed.',
    'missing-input-response': 'The response parameter is missing.',
    'invalid-input-response': 'The response parameter is invalid or malformed.',
    'bad-request': 'The request is invalid or malformed.',
    'timeout-or-duplicate': 'The response is no longer valid: either is too old or has been used previously.',
}


class ReCaptchaException(Exception):
    pass


def validate_recaptcha_token(token: str, original_action: str) -> bool:
    params = {
        "secret": RECAPTCHA_SECRET,
        "response": token
    }
    api_response = requests.post(RECAPTCHA_API_URL, data=params)

    if api_response.status_code != 200:
        raise ReCaptchaException(f"Couldn't reach recaptcha api: {api_response.status_code} {api_response.text}")

    json_response = api_response.json()

    errors_list = []
    for error in json_response.get("error-codes", []):
        if error in RECAPTCHA_ERROR_CODES:
            errors_list.append(RECAPTCHA_ERROR_CODES[error])
        else:
            errors_list.append(error)
    if errors_list:
        raise ReCaptchaException(f"Encountered the following error(s): {errors_list}")

    if json_response["success"]:
        action = json_response.get('action', "")
        if action != original_action:
            raise ReCaptchaException(f"The action '{action}' does not match '{original_action}' from the form")

        score = json_response.get('score', 0)
        return score >= RECAPTCHA_REQUIRED_SCORE

    raise ReCaptchaException("This is not a valid reCAPTCHA token")
