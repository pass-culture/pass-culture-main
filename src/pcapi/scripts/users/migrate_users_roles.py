import logging

from pcapi.core.offerers.models import Offerer
from pcapi.core.users.models import User
from pcapi.core.users.models import UserRole
from pcapi.models import UserOfferer
from pcapi.repository import repository


logger = logging.getLogger(__name__)


def migrate_users_roles() -> None:
    print("Migrating user roles")
    _migrate_admins()
    _migrate_beneficiaries()
    _migrate_pros()
    print("Migration ended")


def _migrate_admins() -> None:
    print("Migrating admins")
    migrated_admins_count = 0
    admins_batch_to_migrate = _get_batch_of_admins_to_migrate()

    while len(admins_batch_to_migrate) > 0:
        for admin_to_migrate in admins_batch_to_migrate:
            admin_to_migrate.add_admin_role()
        repository.save(*admins_batch_to_migrate)

        migrated_admins_count += len(admins_batch_to_migrate)
        admins_batch_to_migrate = _get_batch_of_admins_to_migrate()

    logger.info(
        "Admins migrated", extra={"script": "migrate_users_roles", "migrated_admins_count": migrated_admins_count}
    )


def _migrate_beneficiaries() -> None:
    print("Migrating beneficiaries")
    migrated_beneficiaries_count = 0
    beneficiaries_batch_to_migrate = _get_batch_of_beneficiaries_to_migrate()

    while len(beneficiaries_batch_to_migrate) > 0:
        for beneficiary_to_migrate in beneficiaries_batch_to_migrate:
            beneficiary_to_migrate.add_beneficiary_role()
        repository.save(*beneficiaries_batch_to_migrate)

        migrated_beneficiaries_count += len(beneficiaries_batch_to_migrate)
        beneficiaries_batch_to_migrate = _get_batch_of_beneficiaries_to_migrate()

    logger.info(
        "Beneficiaries migrated",
        extra={"script": "migrate_users_roles", "migrated_beneficiaries_count": migrated_beneficiaries_count},
    )


def _migrate_pros() -> None:
    print("Migrating pros")
    migrated_pros_count = 0
    pros_batch_to_migrate = _get_batch_of_pros_to_migrate()

    while len(pros_batch_to_migrate) > 0:
        for pro_to_migrate in pros_batch_to_migrate:
            pro_to_migrate.add_pro_role()
        repository.save(*pros_batch_to_migrate)

        migrated_pros_count += len(pros_batch_to_migrate)
        pros_batch_to_migrate = _get_batch_of_pros_to_migrate()

    logger.info("Pros migrated", extra={"script": "migrate_users_roles", "migrated_pros_count": migrated_pros_count})


def _get_batch_of_admins_to_migrate() -> list[User]:
    return User.query.filter(User.isAdmin).filter(~User.roles.contains([UserRole.ADMIN])).limit(1000).all()


def _get_batch_of_beneficiaries_to_migrate() -> list[User]:
    return User.query.filter(User.isBeneficiary).filter(~User.roles.contains([UserRole.BENEFICIARY])).limit(1000).all()


def _get_batch_of_pros_to_migrate() -> list[User]:
    return (
        User.query.join(UserOfferer, Offerer)
        .filter(UserOfferer.validationToken.is_(None), Offerer.validationToken.is_(None))
        .filter(~User.roles.contains([UserRole.PRO]))
        .limit(1000)
        .all()
    )
