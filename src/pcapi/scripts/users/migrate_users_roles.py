import logging

from sqlalchemy import text
from sqlalchemy.orm import aliased

from pcapi.core.offerers.models import Offerer
from pcapi.core.users.models import User
from pcapi.core.users.models import UserRole
from pcapi.models import UserOfferer
from pcapi.models.db import db
from pcapi.repository import repository


logger = logging.getLogger(__name__)


def migrate_users_roles() -> None:
    print("Migrating user roles")
    _migrate_admins()
    _migrate_beneficiaries()
    _migrate_pros()
    _remove_duplicated_roles()
    _remove_wrong_pro_roles()
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


def _remove_duplicated_roles() -> None:
    print("Remove duplicated roles")
    deduplicated_users_count = 0
    users_to_deduplicate = _get_batch_of_multiple_role_occurences()

    while len(users_to_deduplicate) > 0:
        for user_to_deduplicate in users_to_deduplicate:
            user_to_deduplicate.roles = list(set(user_to_deduplicate.roles))
        repository.save(*users_to_deduplicate)

        deduplicated_users_count += len(users_to_deduplicate)
        users_to_deduplicate = _get_batch_of_multiple_role_occurences()

    logger.info(
        "Roles deduplicated",
        extra={"script": "migrate_users_roles", "deduplicated_users_count": deduplicated_users_count},
    )


def _remove_wrong_pro_roles() -> None:
    print("Remove PRO role of users with unvalidated offerer or attachment")
    corrected_users_count = 0
    users_to_correct = _get_batch_of_users_with_wrong_pro_role()

    while len(users_to_correct) > 0:
        for user_to_correct in users_to_correct:
            user_to_correct.remove_pro_role()
        repository.save(*users_to_correct)

        corrected_users_count += len(users_to_correct)
        users_to_correct = _get_batch_of_users_with_wrong_pro_role()

    logger.info(
        "Pro roles corrected", extra={"script": "migrate_users_roles", "corrected_users_count": corrected_users_count}
    )


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


def _get_batch_of_multiple_role_occurences() -> list[User]:
    textual_sql = text(
        """SELECT id FROM (SELECT (SELECT count(distinct val) FROM ( SELECT unnest(roles) as val ) as u ) as roles_distinct, roles, id FROM "user" WHERE array_length(roles,1)>1 LIMIT 1000) as t WHERE array_length(t.roles, 1)> t.roles_distinct"""
    )
    textual_sql = textual_sql.columns(User.id)
    return User.query.from_statement(textual_sql).all()


def _get_batch_of_users_with_wrong_pro_role() -> list[User]:
    user_alias = aliased(User)
    user_has_validated_offerer_or_attachment = (
        db.session.query(user_alias)
        .join(UserOfferer, UserOfferer.userId == user_alias.id)
        .join(Offerer, Offerer.id == UserOfferer.offererId)
        .filter(User.id == user_alias.id)
        .filter(UserOfferer.validationToken.is_(None), Offerer.validationToken.is_(None))
        .exists()
    )

    return (
        User.query.filter(User.roles.contains([UserRole.PRO]))
        .filter(~user_has_validated_offerer_or_attachment)
        .limit(1000)
        .all()
    )
