from unittest.mock import MagicMock
from unittest.mock import patch

import pytest

from pcapi.connectors.api_demarches_simplifiees import ApiDemarchesSimplifieesException
from pcapi.connectors.api_demarches_simplifiees import DMSGraphQLClient
from pcapi.connectors.api_demarches_simplifiees import GraphQLApplicationStates
from pcapi.connectors.api_demarches_simplifiees import get_all_applications_for_procedure
from pcapi.connectors.api_demarches_simplifiees import get_application_details

from tests.scripts.beneficiary.fixture import make_graphql_application


class GetAllApplicationsForProcedureTest:
    @patch("pcapi.connectors.api_demarches_simplifiees.requests.get")
    def test_load_applications_from_demarche_simplifiee_api_with_right_link(self, requests_get):
        # Given
        response_return_value = MagicMock(status_code=200, text="")
        response_return_value.json = MagicMock(return_value={"test": "value"})
        requests_get.return_value = response_return_value
        procedure_id = 1
        token = "12345"

        # When
        applications_for_procedure = get_all_applications_for_procedure(
            procedure_id=procedure_id, token=token, results_per_page=1000
        )

        # Then
        call_args = requests_get.call_args
        assert call_args[0] == (
            "https://www.demarches-simplifiees.fr/api/v1/procedures/1/dossiers?token=12345&page=1&resultats_par_page=1000",
        )
        assert applications_for_procedure == {"test": "value"}

    @patch("pcapi.connectors.api_demarches_simplifiees.requests.get")
    def test_raises_api_demarches_simplifiees_exception_when_api_status_code_not_200(self, requests_get):
        # Given
        response_return_value = MagicMock(status_code=400, text="")
        response_return_value.json = MagicMock(return_value={})
        requests_get.return_value = response_return_value
        procedure_id = 1
        token = "12345"

        # When
        with pytest.raises(ApiDemarchesSimplifieesException) as exception:
            get_all_applications_for_procedure(procedure_id=procedure_id, token=token)

        # Then
        assert (
            str(exception.value) == "Error getting API démarches simplifiées DATA for procedure_id: 1 and token 12345"
        )


class GetApplicationDetailsTest:
    @patch("pcapi.connectors.api_demarches_simplifiees.requests.get")
    def test_calls_demarche_simplifiee_api_with_right_link(self, requests_get):
        # Given
        response_return_value = MagicMock(status_code=200, text="")
        response_return_value.json = MagicMock(return_value={"test": "value"})
        requests_get.return_value = response_return_value
        procedure_id = 1
        application_id = 2
        token = "12345"

        # When
        application_details = get_application_details(application_id, procedure_id, token)

        # Then
        call_args = requests_get.call_args
        assert call_args[0] == ("https://www.demarches-simplifiees.fr/api/v1/procedures/1/dossiers/2?token=12345",)
        assert application_details == {"test": "value"}


class GraphqlResponseTest:
    @patch.object(DMSGraphQLClient, "execute_query")
    def test_get_applications_with_details(self, execute_query):
        execute_query.side_effect = [
            make_graphql_application(123, "closed", full_graphql_response=True, has_next_page=True),
            make_graphql_application(456, "closed", full_graphql_response=True),
        ]

        client = DMSGraphQLClient()
        results = list(client.get_applications_with_details(123, GraphQLApplicationStates.accepted))
        assert client.execute_query.call_count == 2
        assert len(results) == 2

    @patch.object(DMSGraphQLClient, "execute_query")
    def test_archive_application(self, execute_query):
        technical_id = "RandomApplicationId"

        execute_query.return_value = {"dossierArchiver": {"dossier": {"id": technical_id}, "errors": None}}
        client = DMSGraphQLClient()
        client.archive_application("ApplicationTechnicalId", "InstructorTechId")

        assert client.execute_query.call_count == 1
