import os
from unittest.mock import Mock

from domain.retrieve_bank_account_information_for_offerers import get_all_file_ids_from_demarches_simplifiees_procedure

PROCEDURE_ID = os.environ['DEMARCHES_SIMPLIFIEES_PROCEDURE_ID']
TOKEN = os.environ['DEMARCHES_SIMPLIFIEES_TOKEN']


class GetAllFileIdsFromDemarchesSimplifieesProcedureTest:
    def setup_class(self):
        self.mock_get_all_files_for_procedure = Mock()

    def test_returns_list_of_one_id_when_get_all_files_from_procedure_returns_list_of_one_file_with_state_closed(self):
        # Given
        self.mock_get_all_files_for_procedure.return_value = {
            "dossiers": [
                {"id": 2,
                 "updated_at": "2019-02-04T16:51:18.293Z",
                 "initiated_at": "2019-01-12T10:43:18.735Z",
                 "state": "closed"}
            ]
        }

        # When
        file_ids = get_all_file_ids_from_demarches_simplifiees_procedure(PROCEDURE_ID, TOKEN,
                                                                         get_all_files_for_procedure_in_demarches_simplifiees=self.mock_get_all_files_for_procedure)

        # Then
        assert file_ids == [2]

    def test_returns_list_of_one_id_when_get_all_files_from_procedure_returns_list_of_one_file_with_state_closed_and_other_initiated(self):
        # Given
        self.mock_get_all_files_for_procedure.return_value = {
            "dossiers": [
                {"id": 2,
                 "updated_at": "2019-02-04T16:51:18.293Z",
                 "initiated_at": "2019-01-12T10:43:18.735Z",
                 "state": "closed"},
                {"id": 3,
                 "updated_at": "2019-02-03T16:51:18.293Z",
                 "initiated_at": "2019-01-11T10:43:18.735Z",
                 "state": "initiated"}
            ]
        }

        # When
        file_ids = get_all_file_ids_from_demarches_simplifiees_procedure(PROCEDURE_ID, TOKEN,
                                                                         get_all_files_for_procedure_in_demarches_simplifiees=self.mock_get_all_files_for_procedure)

        # Then
        assert file_ids == [2]

    def test_returns_list_of_one_id_when_get_all_files_from_procedure_returns_list_of_two_files_closed_and_one_in_update_date_range(self):
        # Given
        self.mock_get_all_files_for_procedure.return_value = {
            "dossiers": [
                {"id": 2,
                 "updated_at": "2019-02-04T16:51:18.293Z",
                 "initiated_at": "2019-01-12T10:43:18.735Z",
                 "state": "closed"},
                {"id": 3,
                 "updated_at": "2018-12-17T16:51:18.293Z",
                 "initiated_at": "2018-12-11T10:43:18.735Z",
                 "state": "closed"}
            ]
        }

        # When
        file_ids = get_all_file_ids_from_demarches_simplifiees_procedure(PROCEDURE_ID, TOKEN,
                                                                         get_all_files_for_procedure_in_demarches_simplifiees=self.mock_get_all_files_for_procedure)

        # Then
        assert file_ids == [2]
