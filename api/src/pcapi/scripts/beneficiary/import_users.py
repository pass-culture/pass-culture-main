import csv
from datetime import datetime
import logging
import sys
from typing import Iterable
from typing import Optional

from pcapi import settings
import pcapi.core.payments.api as payments_api
import pcapi.core.users.api as users_api
from pcapi.core.users.models import EligibilityType
from pcapi.core.users.models import User
from pcapi.core.users.models import UserRole
from pcapi.core.users.repository import find_user_by_email
from pcapi.core.users.utils import sanitize_email
from pcapi.repository import repository
from pcapi.routes.serialization.users import ProUserCreationBodyModel


logger = logging.getLogger(__name__)


def _get_birth_date(row: dict) -> datetime:
    return datetime.strptime(row["Date de naissance"], "%Y-%m-%d")


def _create_beneficiary(row: dict, role: Optional[UserRole]) -> User:
    user = users_api.create_account(
        email=sanitize_email(row["Mail"]),
        password=settings.STAGING_TEST_USER_PASSWORD,
        birthdate=_get_birth_date(row),
        is_email_validated=True,
        send_activation_mail=False,
        remote_updates=False,
    )
    if role == UserRole.BENEFICIARY:
        deposit = payments_api.create_deposit(user, "import_users (csv)", eligibility=EligibilityType.AGE18)
        repository.save(deposit)
        user.add_beneficiary_role()
    elif role == UserRole.UNDERAGE_BENEFICIARY:
        deposit = payments_api.create_deposit(
            user, "import_users (csv)", eligibility=EligibilityType.UNDERAGE, age_at_registration=16
        )
        repository.save(deposit)
        user.add_underage_beneficiary_role()
    return user


def _create_pro_user(row: dict) -> User:
    user = users_api.create_pro_user_and_offerer(
        ProUserCreationBodyModel(
            address="1 avenue des pros",
            city="MA VILLE",
            email=row["Mail"],
            name=f'Entreprise {row["Nom"]}',
            password=settings.STAGING_TEST_USER_PASSWORD,
            phoneNumber=row["Téléphone"],
            postalCode=row["Code postal"],
            publicName=f'{row["Prénom"]} {row["Nom"]}',
            siren=row["SIREN"],
            contactOk=True,
        )
    )

    # Validate offerer
    offerer = user.offerers[0]
    offerer.validationToken = None
    offerer.dateValidated = datetime.utcnow()
    repository.save(offerer)

    user.isEmailValidated = True
    user.add_pro_role()

    return user


def create_or_update_users(rows: Iterable[dict]) -> list[User]:
    # The purpose of this function is to recreate test users on
    # staging after the staging database is reset. It's not meant to
    # be used anywhere else, and certainly not on production.
    if settings.IS_PROD:
        raise ValueError("This function is not supposed to be run on production")

    users = []
    for row in rows:
        user = find_user_by_email(row["Mail"])
        if user:
            user.dateOfBirth = _get_birth_date(row)
            user.setPassword(settings.STAGING_TEST_USER_PASSWORD)
        else:
            role = UserRole(row["Role"]) if row["Role"] else None
            if role == UserRole.PRO:
                user = _create_pro_user(row)
            else:
                user = _create_beneficiary(row, role)

        user.lastName = row["Nom"]
        user.firstName = row["Prénom"]
        user.publicName = f"{user.firstName} {user.lastName}"
        user.phoneNumber = row["Téléphone"]
        user.departementCode = row["Département"]
        user.postalCode = row["Code postal"]
        repository.save(user)

        users.append(user)
        logger.info("Created or updated user=%s %s from CSV import", user.id, [role.value for role in user.roles])

    admin = find_user_by_email("admin@example.com")
    if not admin:
        admin = users_api.create_account(
            email="admin@example.com",
            password=settings.STAGING_TEST_USER_PASSWORD,
            birthdate=datetime(1946, 12, 24),
            is_email_validated=True,
            send_activation_mail=False,
            remote_updates=False,
        )
    admin.setPassword(settings.STAGING_TEST_USER_PASSWORD)
    admin.remove_beneficiary_role()
    admin.add_admin_role()
    admin.firstName = "Jeanne"
    admin.lastName = "Admin"
    admin.publicName = f"{user.firstName} {user.lastName}"  # type: ignore [union-attr]
    repository.save(admin)
    logger.info("Created or updated admin user=%s", admin.id)
    return users


def _read_file(csv_file):  # type: ignore [no-untyped-def]
    csv_reader = csv.DictReader(csv_file)
    return create_or_update_users(csv_reader)


if __name__ == "__main__":
    from pcapi.flask_app import app

    if len(sys.argv) != 2:
        raise ValueError("This script requires one argument: the path to the CSV file with users to import")
    csv_file_path = sys.argv[1]
    with open(csv_file_path, encoding="utf-8") as fp:
        with app.app_context():
            new_users = _read_file(fp)
    logger.info("Created or updated %d users from %s", len(new_users), csv_file_path)
