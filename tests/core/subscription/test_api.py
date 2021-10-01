import pytest

import pcapi.core.subscription.api as subscription_api
import pcapi.core.users.factories as users_factories
from pcapi.models import BeneficiaryImport
from pcapi.models import BeneficiaryImportSources
from pcapi.models import ImportStatus


@pytest.mark.usefixtures("db_session")
@pytest.mark.parametrize(
    "import_status",
    [
        ImportStatus.DRAFT,
        ImportStatus.ONGOING,
        ImportStatus.REJECTED,
    ],
)
class AttachBenerificaryImportDetailsTest:
    def test_user_application(self, import_status):
        user = users_factories.UserFactory()
        subscription_api.attach_beneficiary_import_details(
            user, 42, 21, BeneficiaryImportSources.demarches_simplifiees, "random_details", import_status
        )

        beneficiary_import = BeneficiaryImport.query.one()
        assert beneficiary_import.source == BeneficiaryImportSources.demarches_simplifiees.value
        assert beneficiary_import.beneficiary == user
        assert len(beneficiary_import.statuses) == 1

        status = beneficiary_import.statuses[0]
        assert status.detail == "random_details"
        assert status.status == import_status
        assert status.author == None

    def test_user_already_have_jouve_applications(self, import_status):
        user = users_factories.UserFactory()
        users_factories.BeneficiaryImportFactory(beneficiary=user, source=BeneficiaryImportSources.jouve.value)

        subscription_api.attach_beneficiary_import_details(
            user, 42, 21, BeneficiaryImportSources.demarches_simplifiees, "random_details", import_status
        )

        beneficiary_import = BeneficiaryImport.query.all()
        assert len(beneficiary_import) == 2

    def test_user_application_already_have_dms_statuses(self, import_status):
        user = users_factories.UserFactory()
        application_id = 42
        procedure_id = 21
        beneficiary_import = users_factories.BeneficiaryImportFactory(
            beneficiary=user,
            source=BeneficiaryImportSources.demarches_simplifiees.value,
            applicationId=application_id,
            sourceId=procedure_id,
        )
        users_factories.BeneficiaryImportStatusFactory(beneficiaryImport=beneficiary_import)

        subscription_api.attach_beneficiary_import_details(
            user,
            application_id,
            procedure_id,
            BeneficiaryImportSources.demarches_simplifiees,
            "random details",
            import_status,
        )
        beneficiary_import = BeneficiaryImport.query.one()
        assert len(beneficiary_import.statuses) == 2

    def test_user_application_already_have_another_dms_application(self, import_status):
        user = users_factories.UserFactory()
        application_id = 42
        procedure_id = 21
        beneficiary_import = users_factories.BeneficiaryImportFactory(
            beneficiary=user,
            source=BeneficiaryImportSources.demarches_simplifiees.value,
            applicationId=143,
            sourceId=procedure_id,
        )
        users_factories.BeneficiaryImportStatusFactory(beneficiaryImport=beneficiary_import)

        subscription_api.attach_beneficiary_import_details(
            user,
            application_id,
            procedure_id,
            BeneficiaryImportSources.demarches_simplifiees,
            "random details",
            import_status,
        )
        assert BeneficiaryImport.query.count() == 2
