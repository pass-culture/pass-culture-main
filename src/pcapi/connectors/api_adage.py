from pcapi import settings
from pcapi.connectors.serialization.api_adage_serializers import InstitutionalProjectRedactorResponse
from pcapi.utils import requests


class AdageException(Exception):
    pass


class InstitutionalProjectRedactorNotFoundException(AdageException):
    pass


def get_institutional_project_redactor_by_email(email: str) -> InstitutionalProjectRedactorResponse:
    api_url = f"{settings.ADAGE_API_URL}/v1/redacteur-projet/{email}"

    api_response = requests.get(
        api_url,
        headers={
            "X-omogen-api-key": settings.ADAGE_API_KEY,
        },
    )

    if api_response.status_code == 404:
        raise InstitutionalProjectRedactorNotFoundException("Requested email is not a known Project Redactor for Adage")
    if api_response.status_code != 200:
        raise AdageException("Error getting API Adage")

    return InstitutionalProjectRedactorResponse.parse_obj(api_response.json())
