import pytest
from unittest.mock import MagicMock, patch

from connectors.api_demarches_simplifiees import get_all_applications_for_procedure, ApiDemarchesSimplifieesException, \
    get_application_details


@pytest.mark.standalone
class GetAllApplicationsForProcedureTest:
    def test_calls_demarche_simplifiee_api_with_right_link_and_verify_false(self):
        # Given
        response_return_value = MagicMock(status_code=200, text='')
        response_return_value.json = MagicMock(return_value={'test': 'value'})
        procedure_id = 1
        token = '12345'

        # When

        with patch('connectors.api_demarches_simplifiees.requests.get',
                   return_value=response_return_value) as requests_get:
            applications_for_procedure = get_all_applications_for_procedure(procedure_id=procedure_id, token=token)

        call_args = requests_get.call_args
        assert call_args[0] == ('https://www.demarches-simplifiees.fr/api/v1/procedures/1/dossiers?token=12345',)
        assert call_args[1] == {'verify': False}
        assert applications_for_procedure == {'test': 'value'}

    def test_raises_api_demarches_simplifiees_exception_when_api_status_code_not_200(self):
        # Given
        response_return_value = MagicMock(status_code=400, text='')
        response_return_value.json = MagicMock(return_value={})
        procedure_id = 1
        token = '12345'

        # When
        with patch('connectors.api_demarches_simplifiees.requests.get',
                   return_value=response_return_value), pytest.raises(ApiDemarchesSimplifieesException) as exception:
            get_all_applications_for_procedure(procedure_id=procedure_id, token=token)

        # Then
        assert str(
            exception.value) == 'Error getting API démarches simplifiées DATA for procedure_id: 1 and token 12345'


@pytest.mark.standalone
class GetApplicationDetailsTest:
    def test_calls_demarche_simplifiee_api_with_right_link_and_verify_false(self):
        # Given
        response_return_value = MagicMock(status_code=200, text='')
        response_return_value.json = MagicMock(return_value={'test': 'value'})
        procedure_id = 1
        application_id = 2
        token = '12345'

        # When

        with patch('connectors.api_demarches_simplifiees.requests.get',
                   return_value=response_return_value) as requests_get:
            application_details = get_application_details(application_id, procedure_id, token)

        call_args = requests_get.call_args
        assert call_args[0] == ('https://www.demarches-simplifiees.fr/api/v1/procedures/1/dossiers/2?token=12345',)
        assert call_args[1] == {'verify': False}
        assert application_details == {'test': 'value'}

    def test_raises_api_demarches_simplifiees_exception_when_api_status_code_not_200(self):
        # Given
        response_return_value = MagicMock(status_code=400, text='')
        response_return_value.json = MagicMock(return_value={})
        procedure_id = 1
        application_id = 2
        token = '12345'

        # When
        with patch('connectors.api_demarches_simplifiees.requests.get',
                   return_value=response_return_value), pytest.raises(ApiDemarchesSimplifieesException) as exception:
            get_application_details(application_id, procedure_id, token)

        # Then
        assert str(
            exception.value) == 'Error getting API démarches simplifiées DATA for procedure_id: 1, application_id: 2 and token 12345'
