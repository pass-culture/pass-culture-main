import logging

from pcapi.utils import requests


logger = logging.getLogger(__name__)


def get_id_token(client_id: str, auth_token: str, api_service_account: str) -> str | None:
    try:
        id_token_response = requests.post(
            f"https://iamcredentials.googleapis.com/v1/projects/-/serviceAccounts/{api_service_account}:generateIdToken",
            headers={
                "Authorization": f"Bearer {auth_token}",
                "Content-Type": "application/json; charset=utf-8",
            },
            json={"audience": client_id, "includeEmail": "true"},
        )
        id_token = id_token_response.json()["token"]
    except requests.exceptions.InvalidHeader:
        # The auth_token has probably not been changed to a correct value
        logger.info("Check the value of your auth_token")
        return None
    except Exception as exc:  # pylint: disable=broad-except
        logger.info("Could not get id_token", extra={"exc": exc})
        return None
    return id_token
