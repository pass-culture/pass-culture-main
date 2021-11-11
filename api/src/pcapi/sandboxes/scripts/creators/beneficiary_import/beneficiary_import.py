import logging

from pcapi.core.users import factories as users_factories
from pcapi.core.users import models as users_models
from pcapi.models import BeneficiaryImport
from pcapi.models import ImportStatus
from pcapi.repository import repository


logger = logging.getLogger(__name__)


def create_beneficiary_user() -> users_models.User:
    import_status = ImportStatus.CREATED
    beneficiary_user = users_factories.BeneficiaryGrant18Factory(email=f"{import_status.value}@email.com")

    logger.info("created 1 beneficiary user")

    return beneficiary_user


def create_admin_user():
    users_factories.AdminFactory(email="pctest.admin93.0@example.com")
    logger.info("created 1 admin user")


def create_beneficiary_imports(beneficiary_user: users_models.User) -> list[BeneficiaryImport]:
    beneficiary_imports = []
    index_of_beneficiary_imports = 1
    for status in ImportStatus:
        user = beneficiary_user if status == ImportStatus.CREATED else None
        beneficiary_import = users_factories.BeneficiaryImportFactory(
            beneficiary=user, applicationId=index_of_beneficiary_imports
        )
        users_factories.BeneficiaryImportStatusFactory(beneficiaryImport=beneficiary_import, status=status)
        index_of_beneficiary_imports += 1

    repository.save(*beneficiary_imports)
    logger.info("created %i beneficiary imports and status", len(beneficiary_imports))

    return beneficiary_imports


def save_beneficiary_import_sandbox():
    create_admin_user()
    beneficiary_users = create_beneficiary_user()
    create_beneficiary_imports(beneficiary_users)
