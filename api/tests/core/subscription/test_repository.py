import pytest

from pcapi.core.subscription import repository as subscription_repository
from pcapi.core.users import factories as users_factories
from pcapi.models import BeneficiaryImportSources
from pcapi.models.beneficiary_import_status import ImportStatus


pytestmark = pytest.mark.usefixtures("db_session")


class UserBeneficiaryImportTest:
    def test_get_beneficiary_import_for_beneficiary(self):
        """Create 'BeneficiaryImport's with different statuses and check that
        the last one created is the one returned.
        """
        user = users_factories.UserFactory()

        source = BeneficiaryImportSources.demarches_simplifiees.value
        for rejected_import in users_factories.BeneficiaryImportFactory.create_batch(
            3, beneficiary=user, source=source
        ):
            users_factories.BeneficiaryImportStatusFactory(
                beneficiaryImport=rejected_import, status=ImportStatus.REJECTED
            )

        # The created status is set to a random datetime in the past (yesterday at most)
        created_import = users_factories.BeneficiaryImportFactory(beneficiary=user)
        users_factories.BeneficiaryImportStatusFactory(beneficiaryImport=created_import, status=ImportStatus.CREATED)

        latest_created_import = users_factories.BeneficiaryImportFactory(beneficiary=user)
        latest_created_import.setStatus(ImportStatus.CREATED)

        beneficiary_import = subscription_repository.get_beneficiary_import_for_beneficiary(user)
        assert beneficiary_import.id == latest_created_import.id
