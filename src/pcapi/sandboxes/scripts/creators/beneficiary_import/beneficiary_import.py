from typing import List

from pcapi.models import ImportStatus, UserSQLEntity, BeneficiaryImport, BeneficiaryImportSources
from pcapi.repository import repository
from pcapi.model_creators.generic_creators import create_user, create_beneficiary_import
from pcapi.utils.logger import logger


def create_beneficiary_user() -> UserSQLEntity:
    import_status = ImportStatus.CREATED
    beneficiary_user = create_user(email=f'{str(import_status)}@email.com')

    repository.save(beneficiary_user)
    logger.info(f'created 1 beneficiary user')

    return beneficiary_user


def create_admin_user():
    admin_user = create_user(
        can_book_free_offers=False,
        is_admin=True,
        email='pctest.admin93.0@btmx.fr'
    )
    repository.save(admin_user)
    logger.info('created 1 admin user')


def create_beneficiary_imports(beneficiary_user: UserSQLEntity) -> List[BeneficiaryImport]:
    beneficiary_imports = []
    index_of_beneficiary_imports = 1
    for status in ImportStatus:
        user = beneficiary_user if status == ImportStatus.CREATED else None
        beneficiary_imports.append(
            create_beneficiary_import(
                application_id=index_of_beneficiary_imports,
                status=status,
                user=user,
            )
        )
        index_of_beneficiary_imports += 1

    repository.save(*beneficiary_imports)
    logger.info(f'created {len(beneficiary_imports)} beneficiary imports and status')

    return beneficiary_imports


def save_beneficiary_import_sandbox():
    create_admin_user()
    beneficiary_users = create_beneficiary_user()
    create_beneficiary_imports(beneficiary_users)
