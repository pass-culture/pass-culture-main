import datetime
from unittest.mock import patch

import pytest

from pcapi import settings
from pcapi.connectors.dms import factories as ds_factories
from pcapi.connectors.dms import models as ds_models
from pcapi.core.finance.ds import import_ds_bank_information_applications
from pcapi.core.finance.models import BankInformationStatus

from tests.connector_creators import demarches_simplifiees_creators as ds_creators


@pytest.mark.usefixtures("db_session")
class ImportDSBankInformationApplicationsTest:
    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.get_pro_bank_nodes_states")
    @patch("pcapi.core.finance.ds.save_venue_bank_informations.execute")
    def test_import_empty_db(self, mocked_save_venue_bank_informations_execute, mocked_get_pro_bank_nodes):
        mocked_get_pro_bank_nodes.return_value = [
            ds_creators.get_bank_info_response_procedure_v4(),
            ds_creators.get_bank_info_response_procedure_v4(
                dms_token="987654321fedcba", dossier_id="AbLQmfezdf", application_id=10
            ),
        ]

        import_ds_bank_information_applications(procedure_number=settings.DMS_VENUE_PROCEDURE_ID_V4)

        assert mocked_save_venue_bank_informations_execute.call_count == 2
        application_detail_first_call_arg = mocked_save_venue_bank_informations_execute.mock_calls[0].kwargs[
            "application_details"
        ]
        assert application_detail_first_call_arg.status == BankInformationStatus.ACCEPTED
        assert application_detail_first_call_arg.application_id == 9
        assert application_detail_first_call_arg.modification_date == datetime.datetime(2020, 1, 3)
        assert application_detail_first_call_arg.iban == "FR7630007000111234567890144"
        assert application_detail_first_call_arg.bic == "SOGEFRPP"
        assert application_detail_first_call_arg.dms_token == "1234567890abcdef"
        assert application_detail_first_call_arg.dossier_id == "Q2zzbXAtNzgyODAw"
        assert (
            mocked_save_venue_bank_informations_execute.mock_calls[0].kwargs["procedure_id"]
            == settings.DMS_VENUE_PROCEDURE_ID_V4
        )

        application_detail_second_call_arg = mocked_save_venue_bank_informations_execute.mock_calls[1].kwargs[
            "application_details"
        ]
        assert application_detail_second_call_arg.status == BankInformationStatus.ACCEPTED
        assert application_detail_second_call_arg.application_id == 10
        assert application_detail_second_call_arg.modification_date == datetime.datetime(2020, 1, 3)
        assert application_detail_second_call_arg.iban == "FR7630007000111234567890144"
        assert application_detail_second_call_arg.bic == "SOGEFRPP"
        assert application_detail_second_call_arg.dms_token == "987654321fedcba"
        assert application_detail_second_call_arg.dossier_id == "AbLQmfezdf"
        assert (
            mocked_save_venue_bank_informations_execute.mock_calls[1].kwargs["procedure_id"]
            == settings.DMS_VENUE_PROCEDURE_ID_V4
        )

        latest_import = ds_models.LatestDmsImport.query.one()
        assert latest_import.procedureId == int(settings.DMS_VENUE_PROCEDURE_ID_V4)
        assert latest_import.latestImportDatetime
        assert not latest_import.isProcessing
        assert latest_import.processedApplications == [9, 10]

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.get_pro_bank_nodes_states")
    def test_only_call_from_last_update(self, mocked_get_pro_bank_nodes):
        mocked_get_pro_bank_nodes.return_value = []
        previous = ds_factories.LatestDmsImportFactory(procedureId=settings.DMS_VENUE_PROCEDURE_ID_V4)

        import_ds_bank_information_applications(procedure_number=settings.DMS_VENUE_PROCEDURE_ID_V4)

        mocked_get_pro_bank_nodes.assert_called_once_with(
            procedure_number=settings.DMS_VENUE_PROCEDURE_ID_V4, since=previous.latestImportDatetime
        )

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.get_pro_bank_nodes_states")
    def test_only_process_if_previous_ended(self, mocked_get_pro_bank_nodes):
        ds_factories.LatestDmsImportFactory(
            procedureId=settings.DMS_VENUE_PROCEDURE_ID_V4,
            isProcessing=True,
        )

        import_ds_bank_information_applications(procedure_number=settings.DMS_VENUE_PROCEDURE_ID_V4)

        mocked_get_pro_bank_nodes.assert_not_called()

    @patch("pcapi.connectors.dms.api.DMSGraphQLClient.get_pro_bank_nodes_states")
    def test_reset_import_if_stuck(self, mocked_get_pro_bank_nodes):
        latest_import = ds_factories.LatestDmsImportFactory(
            procedureId=settings.DMS_VENUE_PROCEDURE_ID_V4,
            isProcessing=True,
            latestImportDatetime=datetime.datetime.utcnow() - datetime.timedelta(days=2),
        )

        import_ds_bank_information_applications(procedure_number=settings.DMS_VENUE_PROCEDURE_ID_V4)

        assert not latest_import.isProcessing
