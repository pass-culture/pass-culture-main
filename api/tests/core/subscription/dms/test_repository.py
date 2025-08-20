import datetime
from unittest.mock import patch

import pytest

from pcapi.connectors.dms import api as dms_api
from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
from pcapi.core.subscription.dms import repository as dms_repository

from tests.scripts.beneficiary.fixture import make_graphql_deleted_applications
from tests.scripts.beneficiary.fixture import make_parsed_graphql_application


@pytest.mark.usefixtures("db_session")
class RepositoryUnitTest:
    def test_get_orphan_dms_application_by_application_id(self):
        fraud_factories.OrphanDmsApplicationFactory(application_id=88)
        assert dms_repository.get_orphan_dms_application_by_application_id(88) is not None
        assert dms_repository.get_orphan_dms_application_by_application_id(99) is None

    def test_create_orphan_dms_application(self):
        dms_repository.create_orphan_dms_application(
            application_number=88,
            procedure_number=99,
            latest_modification_datetime=datetime.datetime.utcnow(),
            email="john.stiles@example.com",
        )
        assert dms_repository.get_orphan_dms_application_by_application_id(88) is not None


class GetAlreadyProcessedApplicationIdTest:
    @pytest.mark.usefixtures("db_session")
    def test_already_processed_application_numbers(self):
        content = fraud_factories.DMSContentFactory(application_number=8888, procedure_number=123)
        fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId=8888,
            resultContent=content,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.OK,
        )

        # Orphan application
        fraud_factories.OrphanDmsFraudCheckFactory(application_id=9999, process_id=123)
        fraud_factories.OrphanDmsFraudCheckFactory(application_id=9991, process_id=321)

        # Different procedure
        content = fraud_factories.DMSContentFactory(application_number=1111, procedure_number=2)
        fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId=1111,
            resultContent=content,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.OK,
        )

        # No Content
        fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId=2222,
            resultContent=None,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.ERROR,
        )

        application_numbers = dms_repository._get_already_processed_applications_ids(123)
        assert application_numbers == {8888, 9999, 2222}

    @pytest.mark.usefixtures("db_session")
    def test_already_processed_application_numbers_with_all_fraud_checks_status(self):
        content = fraud_factories.DMSContentFactory(application_number=1111, procedure_number=123)
        fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId=1111,
            resultContent=content,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.KO,
        )
        content = fraud_factories.DMSContentFactory(application_number=2222, procedure_number=123)
        fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId=2222,
            resultContent=content,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.OK,
        )
        content = fraud_factories.DMSContentFactory(application_number=3333, procedure_number=123)
        fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId=3333,
            resultContent=content,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.STARTED,
        )
        content = fraud_factories.DMSContentFactory(application_number=4444, procedure_number=123)
        fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId=4444,
            resultContent=content,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.SUSPICIOUS,
        )
        content = fraud_factories.DMSContentFactory(application_number=5555, procedure_number=123)
        fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId=5555,
            resultContent=content,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.PENDING,
        )
        content = fraud_factories.DMSContentFactory(application_number=6666, procedure_number=123)
        fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId=6666,
            resultContent=content,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.CANCELED,
        )
        content = fraud_factories.DMSContentFactory(application_number=7777, procedure_number=123)
        fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId=7777,
            resultContent=content,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.ERROR,
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId=8888,
            resultContent=None,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.ERROR,
        )

        application_numbers = dms_repository._get_already_processed_applications_ids(123)

        assert application_numbers == {1111, 2222, 4444, 6666, 7777, 8888}


@pytest.mark.usefixtures("db_session")
class ArchiveDMSApplicationsTest:
    @patch.object(dms_api.DMSGraphQLClient, "get_applications_with_details")
    @patch.object(dms_api.DMSGraphQLClient, "archive_application")
    @pytest.mark.settings(DMS_ENROLLMENT_INSTRUCTOR="SomeInstructorId")
    def test_archive_applications(self, dms_archive, dms_applications):
        to_archive_applications_id = 123
        pending_applications_id = 456
        procedure_number = 1

        content = fraud_factories.DMSContentFactory(procedure_number=procedure_number)
        fraud_factories.BeneficiaryFraudCheckFactory(
            resultContent=content,
            status=fraud_models.FraudCheckStatus.OK,
            type=fraud_models.FraudCheckType.DMS,
            thirdPartyId=str(to_archive_applications_id),
        )
        fraud_factories.BeneficiaryFraudCheckFactory(
            resultContent=content,
            status=fraud_models.FraudCheckStatus.STARTED,
            type=fraud_models.FraudCheckType.DMS,
            thirdPartyId=str(pending_applications_id),
        )
        dms_applications.return_value = [
            make_parsed_graphql_application(
                to_archive_applications_id, "accepte", application_techid="TO_ARCHIVE_TECHID"
            ),
            make_parsed_graphql_application(pending_applications_id, "accepte", application_techid="PENDING_ID"),
        ]

        dms_repository.archive_applications(procedure_number, dry_run=False)

        dms_archive.assert_called_once()
        assert dms_archive.call_args[0] == ("TO_ARCHIVE_TECHID", "SomeInstructorId")


class HandleDeletedDmsApplicationsTest:
    @pytest.mark.usefixtures("db_session")
    @patch.object(dms_api.DMSGraphQLClient, "execute_query")
    def test_handle_deleted_dms_applications(self, execute_query):
        fraud_check_not_to_mark_as_deleted = fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId="1", type=fraud_models.FraudCheckType.DMS
        )
        fraud_check_to_mark_as_deleted = fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId="2", type=fraud_models.FraudCheckType.DMS
        )
        fraud_check_already_marked_as_deleted = fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId="3",
            status=fraud_models.FraudCheckStatus.CANCELED,
            reason="Custom reason",
            type=fraud_models.FraudCheckType.DMS,
        )
        fraud_check_to_delete_with_empty_result_content = fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId="4", type=fraud_models.FraudCheckType.DMS, resultContent=None
        )
        ok_fraud_check_not_to_mark_as_deleted = fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId="5", type=fraud_models.FraudCheckType.DMS, status=fraud_models.FraudCheckStatus.OK
        )

        procedure_number = 1
        execute_query.return_value = make_graphql_deleted_applications(procedure_number, [2, 3, 4])

        dms_repository.handle_deleted_dms_applications(procedure_number)

        assert fraud_check_not_to_mark_as_deleted.status == fraud_models.FraudCheckStatus.PENDING
        assert fraud_check_to_mark_as_deleted.status == fraud_models.FraudCheckStatus.CANCELED
        assert fraud_check_already_marked_as_deleted.status == fraud_models.FraudCheckStatus.CANCELED
        assert fraud_check_to_delete_with_empty_result_content.status == fraud_models.FraudCheckStatus.CANCELED
        assert ok_fraud_check_not_to_mark_as_deleted.status == fraud_models.FraudCheckStatus.OK

        assert (
            fraud_check_to_delete_with_empty_result_content.reason
            == "Dossier supprimé sur démarches-simplifiées. Motif: user_request"
        )
        assert (
            fraud_check_to_mark_as_deleted.reason == "Dossier supprimé sur démarches-simplifiées. Motif: user_request"
        )
        assert fraud_check_already_marked_as_deleted.reason == "Custom reason"

        assert fraud_check_not_to_mark_as_deleted.resultContent.get("deletion_datetime") is None
        assert fraud_check_to_mark_as_deleted.resultContent.get("deletion_datetime") == "2021-10-01T22:00:00"
        assert fraud_check_to_delete_with_empty_result_content.resultContent is None

    @pytest.mark.usefixtures("db_session")
    @patch.object(dms_api.DMSGraphQLClient, "execute_query")
    def test_get_latest_deleted_application_datetime(self, execute_query):
        procedure_number = 1
        latest_deletion_date = datetime.datetime(2020, 1, 1)

        dms_content_with_deletion_date = fraud_factories.DMSContentFactory(
            deletion_datetime=latest_deletion_date, procedure_number=procedure_number
        )
        dms_content_before_deletion_date = fraud_factories.DMSContentFactory(
            deletion_datetime=latest_deletion_date - datetime.timedelta(days=1), procedure_number=procedure_number
        )

        # fraud_check_deleted_last
        fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId="8888",
            status=fraud_models.FraudCheckStatus.CANCELED,
            type=fraud_models.FraudCheckType.DMS,
            resultContent=dms_content_with_deletion_date,
        )
        # fraud_check_deleted_before_last
        fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId="8889",
            status=fraud_models.FraudCheckStatus.CANCELED,
            type=fraud_models.FraudCheckType.DMS,
            resultContent=dms_content_before_deletion_date,
        )
        # fraud_check_with_empty_result_content
        fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId="8890",
            status=fraud_models.FraudCheckStatus.CANCELED,
            type=fraud_models.FraudCheckType.DMS,
            resultContent=None,
        )

        execute_query.return_value = make_graphql_deleted_applications(procedure_number, [8888, 8889, 8890])

        assert dms_repository._get_latest_deleted_application_datetime(procedure_number) == latest_deletion_date
