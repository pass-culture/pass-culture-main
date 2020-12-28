import requests

from pcapi import settings


class ScalingoApiException(Exception):
    pass


def run_process_in_one_off_container(command: str) -> str:
    app_bearer_token = _get_application_bearer_token()
    run_one_off_endpoint = f"/apps/{settings.API_APPLICATION_NAME}/run"
    command_parameters = {
        "command": command,
        "region": settings.SCALINGO_API_REGION,
        "detached": True,
        "size": settings.SCALINGO_API_CONTAINER_SIZE,
    }
    api_response = requests.post(
        f"{settings.SCALINGO_API_URL}{run_one_off_endpoint}",
        json=command_parameters,
        headers={"Authorization": f"Bearer {app_bearer_token}"},
    )
    if api_response.status_code != 200:
        raise ScalingoApiException(f"Error getting bearer token with status {api_response.status_code}")
    json_response = api_response.json()
    return json_response["container"]["id"]


def _get_application_bearer_token() -> str:
    application_token = settings.SCALINGO_APP_TOKEN
    bearer_token_endpoint = "/tokens/exchange"
    api_response = requests.post(f"{settings.SCALINGO_AUTH_URL}{bearer_token_endpoint}", auth=(None, application_token))
    if api_response.status_code != 200:
        raise ScalingoApiException(f"Error getting bearer token with status {api_response.status_code}")
    json_response = api_response.json()
    return json_response["token"]
