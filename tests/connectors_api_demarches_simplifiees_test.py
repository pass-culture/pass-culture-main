import pytest
from unittest.mock import MagicMock, patch

from connectors.api_demarches_simplifiees import get_all_files_for_procedure, ApiDemarchesSimplifieesException


# def test_get_all_files_by_procedure_id():
#     # Given
#     mocked_api_json = {"dossiers": [
#         {"id": 1, "updated_at": "2019-01-04T15:41:18.293Z", "initiated_at": "2019-01-03T10:43:18.735Z",
#          "state": "closed"},
#         {"id": 2, "updated_at": "2019-02-04T15:52:26.287Z", "initiated_at": "2019-02-04T15:52:23.935Z",
#          "state": "initiated"}]}
#
#     response = MagicMock(status_code=200, text='')
#     response.json = MagicMock(return_value=mocked_api_json)
#
#
#     # When
#     files = get_all_files_id_by_procedure_id(procedure_id)
#
#     # Then


@pytest.mark.standalone
class GetAllFilesForProcedureTest:
    def test_calls_demarche_simplifiee_api_with_right_link_and_verify_false(self):
        # Given
        response_return_value = MagicMock(status_code=200, text='')
        response_return_value.json = MagicMock(return_value={})
        procedure_id = 1
        token = '12345'

        # When

        with patch('connectors.api_demarches_simplifiees.requests.get',
                   return_value=response_return_value) as requests_get:
            get_all_files_for_procedure(procedure_id=procedure_id, token=token)

        call_args = requests_get.call_args
        assert call_args[0] == ('https://www.demarches-simplifiees.fr/api/v1/procedures/1/dossiers?token=12345',)
        assert call_args[1] == {'verify': False}

    def test_raises_api_demarches_simplifiees_exception_when_api_status_code_not_200(self):
        # Given
        response_return_value = MagicMock(status_code=400, text='')
        response_return_value.json = MagicMock(return_value={})
        procedure_id = 1
        token = '12345'

        # When
        with patch('connectors.api_demarches_simplifiees.requests.get',
                   return_value=response_return_value), pytest.raises(ApiDemarchesSimplifieesException) as exception:
            get_all_files_for_procedure(procedure_id=procedure_id, token=token)

        # Then
        assert str(exception.value) == 'Error getting API démarches simplifiées DATA for procedure_id : 1 and token 12345'
