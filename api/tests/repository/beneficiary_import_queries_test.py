from datetime import datetime
from datetime import timedelta

from freezegun import freeze_time
import pytest

from pcapi.core.fraud import factories as fraud_factories
from pcapi.core.fraud import models as fraud_models
from pcapi.core.users import factories as users_factories
from pcapi.core.users.models import EligibilityType
from pcapi.models.beneficiary_import import BeneficiaryImport
from pcapi.models.beneficiary_import import BeneficiaryImportSources
from pcapi.models.beneficiary_import_status import ImportStatus
from pcapi.repository.beneficiary_import_queries import get_already_processed_applications_ids
from pcapi.repository.beneficiary_import_queries import save_beneficiary_import_with_status


class SaveBeneficiaryImportWithStatusTest:
    @pytest.mark.usefixtures("db_session")
    def test_a_status_is_set_on_a_new_import(self, app):
        # when
        save_beneficiary_import_with_status(
            ImportStatus.DUPLICATE,
            123,
            source=BeneficiaryImportSources.demarches_simplifiees,
            source_id=14562,
            user=None,
            eligibility_type=None,
        )

        # then
        beneficiary_import = BeneficiaryImport.query.filter_by(applicationId=123).first()
        assert beneficiary_import.currentStatus == ImportStatus.DUPLICATE

    @pytest.mark.usefixtures("db_session")
    def test_a_beneficiary_import_is_saved_with_all_fields(self, app):
        # when
        save_beneficiary_import_with_status(
            ImportStatus.DUPLICATE,
            123,
            source=BeneficiaryImportSources.demarches_simplifiees,
            source_id=145236,
            user=None,
            eligibility_type=EligibilityType.AGE18,
        )

        # then
        beneficiary_import = BeneficiaryImport.query.filter_by(applicationId=123).first()
        assert beneficiary_import.applicationId == 123
        assert beneficiary_import.sourceId == 145236
        assert beneficiary_import.source == "demarches_simplifiees"
        assert beneficiary_import.eligibilityType == EligibilityType.AGE18

    @pytest.mark.usefixtures("db_session")
    def test_a_status_is_set_on_an_existing_import(self, app):
        # given
        two_days_ago = datetime.utcnow() - timedelta(days=2)
        with freeze_time(two_days_ago):
            save_beneficiary_import_with_status(
                ImportStatus.DUPLICATE,
                123,
                source=BeneficiaryImportSources.demarches_simplifiees,
                source_id=14562,
                user=None,
                eligibility_type=None,
            )
        beneficiary = users_factories.BeneficiaryGrant18Factory()

        # when
        save_beneficiary_import_with_status(
            ImportStatus.CREATED,
            123,
            source=BeneficiaryImportSources.demarches_simplifiees,
            source_id=14562,
            user=beneficiary,
            eligibility_type=None,
        )

        # then
        beneficiary_imports = BeneficiaryImport.query.filter_by(applicationId=123).all()
        assert len(beneficiary_imports) == 1
        assert beneficiary_imports[0].currentStatus == ImportStatus.CREATED
        assert beneficiary_imports[0].beneficiary == beneficiary

    @pytest.mark.usefixtures("db_session")
    def test_should_not_delete_beneficiary_when_import_already_exists(self, app):
        # Given
        two_days_ago = datetime.utcnow() - timedelta(days=2)
        beneficiary = users_factories.BeneficiaryGrant18Factory()
        with freeze_time(two_days_ago):
            save_beneficiary_import_with_status(
                ImportStatus.CREATED,
                123,
                source=BeneficiaryImportSources.demarches_simplifiees,
                source_id=14562,
                user=beneficiary,
                eligibility_type=None,
            )

        # When
        save_beneficiary_import_with_status(
            ImportStatus.REJECTED,
            123,
            source=BeneficiaryImportSources.demarches_simplifiees,
            source_id=14562,
            user=None,
            eligibility_type=None,
        )

        # Then
        beneficiary_imports = BeneficiaryImport.query.filter_by(applicationId=123).first()
        assert beneficiary_imports.beneficiary == beneficiary


@pytest.mark.usefixtures("db_session")
class GetAlreadyProcessedApplicationIdTest:
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
