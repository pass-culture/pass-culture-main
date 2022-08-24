import datetime
from unittest.mock import patch

import pytest

from pcapi.connectors.dms import api as dms_connector_api
from pcapi.connectors.dms import factories as dms_factories
from pcapi.connectors.dms import models as dms_models
from pcapi.core.fraud import models as fraud_models
import pcapi.core.users.factories as users_factories
from pcapi.scripts.subscription.dms.import_dms_accepted_applications import import_all_updated_dms_applications

from tests.scripts.beneficiary import fixture


class DmsImportTest:
    @pytest.mark.usefixtures("db_session")
    @patch.object(dms_connector_api.DMSGraphQLClient, "get_applications_with_details")
    def test_initialize_latest_import_datetime(self, mock_get_applications_with_details):
        mock_get_applications_with_details.return_value = [
            fixture.make_parsed_graphql_application(
                123,
                "accepte",
                email="email1@example.com",
                id_piece_number="123123121",
                last_modification_date="2020-10-01T20:00:00+02:00",
                procedure_number=1,
            ),
            fixture.make_parsed_graphql_application(
                456,
                "en_construction",
                email="email2@example.com",
                id_piece_number="123123122",
                last_modification_date="2020-10-01T20:10:00+02:00",
                procedure_number=1,
            ),
        ]
        user = users_factories.UserFactory(email="email1@example.com")
        import_all_updated_dms_applications(1)
        user_dms_fraud_check = [
            fraud_check
            for fraud_check in user.beneficiaryFraudChecks
            if fraud_check.type == fraud_models.FraudCheckType.DMS
        ][0]
        orphan_dms_application = fraud_models.OrphanDmsApplication.query.first()
        latest_import_record = dms_models.LatestDmsImport.query.first()

        assert mock_get_applications_with_details.call_count == 3  # 1 call for each state
        assert user_dms_fraud_check.status == fraud_models.FraudCheckStatus.OK
        assert user_dms_fraud_check.type == fraud_models.FraudCheckType.DMS

        assert orphan_dms_application.email == "email2@example.com"

        assert latest_import_record.procedureId == 1
        assert latest_import_record.latestImportDatetime == datetime.datetime(2020, 10, 1, 18, 10, 0)

    @pytest.mark.usefixtures("db_session")
    @patch.object(dms_connector_api.DMSGraphQLClient, "get_applications_with_details")
    def test_second_import_of_same_procedure_updates_latest_import_datetime(self, mock_get_applications_with_details):
        mock_get_applications_with_details.return_value = [
            fixture.make_parsed_graphql_application(
                123,
                "accepte",
                email="email1@example.com",
                id_piece_number="123123121",
                last_modification_date="2020-10-01T20:00:00+02:00",
                procedure_number=1,
            ),
            fixture.make_parsed_graphql_application(
                456,
                "en_construction",
                email="email2@example.com",
                id_piece_number="123123122",
                last_modification_date="2020-10-01T21:00:00+02:00",
                procedure_number=1,
            ),
        ]
        dms_factories.LatestDmsImportFactory(
            procedureId=1, latestImportDatetime=datetime.datetime(2020, 10, 1, 15, 0, 0)
        )

        import_all_updated_dms_applications(1)

        latest_import_record = dms_models.LatestDmsImport.query.order_by(
            dms_models.LatestDmsImport.latestImportDatetime.desc()
        ).first()
        assert latest_import_record.latestImportDatetime == datetime.datetime(2020, 10, 1, 19, 0, 0)
        mock_get_applications_with_details.assert_called_once_with(1, since=datetime.datetime(2020, 10, 1, 15, 0))

    @pytest.mark.usefixtures("db_session")
    @patch.object(dms_connector_api.DMSGraphQLClient, "get_applications_with_details")
    def test_import_is_cancelled_if_another_is_already_in_progress(self, mock_get_applications_with_details):
        dms_factories.LatestDmsImportFactory(procedureId=1, isProcessing=True)

        import_all_updated_dms_applications(1)

        assert dms_models.LatestDmsImport.query.count() == 1
        mock_get_applications_with_details.assert_not_called()

    @pytest.mark.usefixtures("db_session")
    @patch.object(dms_connector_api.DMSGraphQLClient, "get_applications_with_details")
    def test_latest_import_datetime_stays_the_same_when_no_import_happened(self, mock_get_applications_with_details):
        dms_factories.LatestDmsImportFactory(procedureId=1, latestImportDatetime=datetime.datetime(2020, 10, 1, 15, 0))

        import_all_updated_dms_applications(1)

        latest_import_record = dms_models.LatestDmsImport.query.first()
        assert latest_import_record.latestImportDatetime == datetime.datetime(2020, 10, 1, 15, 0)
