import pytest
import requests_mock

from pcapi.connectors.api_adage import AdageException
from pcapi.connectors.api_adage import InstitutionalProjectRedactorNotFoundException
from pcapi.connectors.api_adage import get_institutional_project_redactor_by_email
from pcapi.connectors.serialization.api_adage_serializers import InstitutionalProjectRedactorResponse
from pcapi.core.testing import override_settings


class GetInstitutionalProjectRedactorByEmailTest:
    @override_settings(ADAGE_API_URL="https://adage-api-url")
    @override_settings(ADAGE_API_KEY="adage-api-key")
    def test_should_return_request_response_from_api(self):
        # Given
        institutional_project_redactor_email = "project.redactor@example.com"
        response = {
            "civilite": "Mme",
            "nom": "Redactor",
            "prenom": "Project",
            "mail": institutional_project_redactor_email,
            "etablissements": [{"uai": "XXXXXXXXX", "nom": "LYCÉE JEAN - SAINT-NAZAIRE"}],
        }

        # When
        with requests_mock.Mocker() as request_mock:
            request_mock.get(
                f"https://adage-api-url/v1/redacteur-projet/{institutional_project_redactor_email}",
                request_headers={
                    "X-omogen-api-key": "adage-api-key",
                },
                json=response,
            )
            institutional_project_redactor_informations = get_institutional_project_redactor_by_email(
                institutional_project_redactor_email
            )

        # Then
        assert isinstance(institutional_project_redactor_informations, InstitutionalProjectRedactorResponse)
        assert institutional_project_redactor_informations.email == institutional_project_redactor_email
        assert institutional_project_redactor_informations.civility == response["civilite"]
        assert institutional_project_redactor_informations.first_name == response["prenom"]
        assert institutional_project_redactor_informations.last_name == response["nom"]
        educational_institutions = institutional_project_redactor_informations.educational_institutions
        assert len(educational_institutions) == 1
        assert educational_institutions[0].uai == response["etablissements"][0]["uai"]
        assert educational_institutions[0].name == response["etablissements"][0]["nom"]

    @override_settings(ADAGE_API_URL="https://adage-api-url")
    @override_settings(ADAGE_API_KEY="adage-api-key")
    def test_should_raise_exception_when_api_call_fails(self):
        # Given
        institutional_project_redactor_email = "project.redactor@example.com"
        adage_error_message = "Something went wrong"

        # When
        with pytest.raises(AdageException) as exception:
            with requests_mock.Mocker() as request_mock:
                request_mock.get(
                    f"https://adage-api-url/v1/redacteur-projet/{institutional_project_redactor_email}",
                    request_headers={
                        "X-omogen-api-key": "adage-api-key",
                    },
                    text=adage_error_message,
                    status_code=400,
                )
                get_institutional_project_redactor_by_email(institutional_project_redactor_email)

        # Then
        assert str(exception.value.message) == "Error getting Adage API"
        assert str(exception.value.status_code) == "400"
        assert exception.value.response_text == adage_error_message

    @override_settings(ADAGE_API_URL="https://adage-api-url")
    @override_settings(ADAGE_API_KEY="adage-api-key")
    def test_should_raise_InstitutionalProjectRedactorNotFound_when_adage_does_not_know_the_email(self):
        # Given
        unknown_email = "unknown.project.redactor@example.com"

        # When
        with pytest.raises(InstitutionalProjectRedactorNotFoundException) as exception:
            with requests_mock.Mocker() as request_mock:
                request_mock.get(
                    f"https://adage-api-url/v1/redacteur-projet/{unknown_email}",
                    request_headers={
                        "X-omogen-api-key": "adage-api-key",
                    },
                    status_code=404,
                )
                get_institutional_project_redactor_by_email(unknown_email)

        # Then
        assert str(exception.value) == "Requested email is not a known Project Redactor for Adage"
