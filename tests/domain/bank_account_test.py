from datetime import datetime
from unittest.mock import Mock

from domain.bank_account import \
    get_all_application_ids_from_demarches_simplifiees_procedure


class GetAllFileIdsFromDemarchesSimplifieesProcedureTest:
    def setup_class(self):
        self.PROCEDURE_ID = '123456789'
        self.TOKEN = 'AZERTY123/@.,!é'
        self.mock_get_all_applications_for_procedure = Mock()

    def test_returns_applications_with_state_closed_only(
            self):
        # Given
        self.mock_get_all_applications_for_procedure.return_value = {
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
        application_ids = get_all_application_ids_from_demarches_simplifiees_procedure(
            self.PROCEDURE_ID, self.TOKEN, datetime(2019, 1, 1),
            get_all_applications=self.mock_get_all_applications_for_procedure
        )

        # Then
        assert application_ids == [2]

    def test_returns_applications_updated_after_last_update_in_database_only(
            self):
        # Given
        self.mock_get_all_applications_for_procedure.return_value = {
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
        application_ids = get_all_application_ids_from_demarches_simplifiees_procedure(
            self.PROCEDURE_ID, self.TOKEN, datetime(2019, 1, 1),
            get_all_applications=self.mock_get_all_applications_for_procedure
        )

        # Then
        assert application_ids == [2]

    def test_returns_list_of_ids_ordered_by_updated_at_asc(
            self):
        # Given
        self.mock_get_all_applications_for_procedure.return_value = {
            "dossiers": [
                {"id": 1,
                 "updated_at": "2019-02-04T16:51:18.293Z",
                 "initiated_at": "2019-01-12T10:43:18.735Z",
                 "state": "closed"},
                {"id": 2,
                 "updated_at": "2018-12-17T16:51:18.293Z",
                 "initiated_at": "2018-12-11T10:43:18.735Z",
                 "state": "closed"},
                {"id": 3,
                 "updated_at": "2018-11-17T16:51:18.293Z",
                 "initiated_at": "2018-12-11T10:43:18.735Z",
                 "state": "closed"},
                {"id": 4,
                 "updated_at": "2019-02-17T16:51:18.293Z",
                 "initiated_at": "2018-12-11T10:43:18.735Z",
                 "state": "closed"}
            ]
        }

        # When
        application_ids = get_all_application_ids_from_demarches_simplifiees_procedure(
            self.PROCEDURE_ID, self.TOKEN, datetime(2018, 1, 1),
            get_all_applications=self.mock_get_all_applications_for_procedure
        )

        # Then
        assert application_ids == [3, 2, 1, 4]
