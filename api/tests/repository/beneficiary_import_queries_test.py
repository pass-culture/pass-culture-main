import pytest

from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
from pcapi.core.subscription.dms.api import get_already_processed_applications_ids
from pcapi.core.users import factories as users_factories
from pcapi.models.beneficiary_import_status import ImportStatus


class GetAlreadyProcessedApplicationIdTest:
    @pytest.mark.usefixtures("db_session")
    def test_already_processed_application_ids(self):
        procedure_id = 123

        draft = users_factories.BeneficiaryImportStatusFactory(
            beneficiaryImport__sourceId=procedure_id,
            status=ImportStatus.DRAFT,
        )

        ongoing = users_factories.BeneficiaryImportStatusFactory(
            beneficiaryImport__sourceId=procedure_id,
            status=ImportStatus.ONGOING,
        )
        duplicate = users_factories.BeneficiaryImportStatusFactory(
            beneficiaryImport__sourceId=procedure_id,
            status=ImportStatus.DUPLICATE,
        )
        error = users_factories.BeneficiaryImportStatusFactory(
            beneficiaryImport__sourceId=procedure_id,
            status=ImportStatus.ERROR,
        )
        created = users_factories.BeneficiaryImportStatusFactory(
            beneficiaryImport__sourceId=procedure_id,
            status=ImportStatus.CREATED,
        )

        rejected = users_factories.BeneficiaryImportStatusFactory(
            beneficiaryImport__sourceId=procedure_id,
            status=ImportStatus.REJECTED,
        )
        retry = users_factories.BeneficiaryImportStatusFactory(
            beneficiaryImport__sourceId=procedure_id,
            status=ImportStatus.RETRY,
        )
        without_continuation = users_factories.BeneficiaryImportStatusFactory(
            beneficiaryImport__sourceId=procedure_id,
            status=ImportStatus.WITHOUT_CONTINUATION,
        )

        application_ids = get_already_processed_applications_ids(procedure_id)
        assert draft.beneficiaryImport.applicationId not in application_ids
        assert ongoing.beneficiaryImport.applicationId not in application_ids
        assert without_continuation.beneficiaryImport.applicationId not in application_ids
        assert retry.beneficiaryImport.applicationId not in application_ids

        assert rejected.beneficiaryImport.applicationId in application_ids
        assert error.beneficiaryImport.applicationId in application_ids
        assert created.beneficiaryImport.applicationId in application_ids
        assert duplicate.beneficiaryImport.applicationId in application_ids

    @pytest.mark.usefixtures("db_session")
    def test_already_processed_application_ids_right_procedure(self):
        created = users_factories.BeneficiaryImportStatusFactory(
            beneficiaryImport__sourceId=123,
            status=ImportStatus.CREATED,
        )

        another_procedure = users_factories.BeneficiaryImportStatusFactory(
            beneficiaryImport__sourceId=456,
            status=ImportStatus.CREATED,
        )

        application_ids = get_already_processed_applications_ids(123)
        assert created.beneficiaryImport.applicationId in application_ids
        assert another_procedure.beneficiaryImport.applicationId not in application_ids

    @pytest.mark.usefixtures("db_session")
    def test_already_processed_application_ids_with_fraud_checks(self):
        # Regular application
        content = fraud_factories.DMSContentFactory(application_id=8888, procedure_id=123)
        fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId=8888,
            resultContent=content,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.OK,
        )

        # Orphan application, Orphan application
        fraud_factories.OrphanDmsFraudCheckFactory(application_id=9999, process_id=123)

        # Different procedure
        content = fraud_factories.DMSContentFactory(application_id=1111, procedure_id=000)
        fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId=1111,
            resultContent=content,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.OK,
        )

        application_ids = get_already_processed_applications_ids(123)
        assert application_ids == {8888, 9999}

    @pytest.mark.usefixtures("db_session")
    def test_already_processed_application_ids_with_all_fraud_checks_status(self):
        content = fraud_factories.DMSContentFactory(application_id=1111, procedure_id=123)
        fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId=1111,
            resultContent=content,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.KO,
        )
        content = fraud_factories.DMSContentFactory(application_id=2222, procedure_id=123)
        fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId=2222,
            resultContent=content,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.OK,
        )
        content = fraud_factories.DMSContentFactory(application_id=3333, procedure_id=123)
        fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId=3333,
            resultContent=content,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.STARTED,
        )
        content = fraud_factories.DMSContentFactory(application_id=4444, procedure_id=123)
        fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId=4444,
            resultContent=content,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.SUSPICIOUS,
        )
        content = fraud_factories.DMSContentFactory(application_id=5555, procedure_id=123)
        fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId=5555,
            resultContent=content,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.PENDING,
        )
        content = fraud_factories.DMSContentFactory(application_id=6666, procedure_id=123)
        fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId=6666,
            resultContent=content,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.CANCELED,
        )
        content = fraud_factories.DMSContentFactory(application_id=7777, procedure_id=123)
        fraud_factories.BeneficiaryFraudCheckFactory(
            thirdPartyId=7777,
            resultContent=content,
            type=fraud_models.FraudCheckType.DMS,
            status=fraud_models.FraudCheckStatus.ERROR,
        )

        application_ids = get_already_processed_applications_ids(123)

        assert application_ids == {1111, 2222, 4444, 6666, 7777}
