import argparse
import csv
from datetime import datetime
from io import TextIOWrapper
import logging
from typing import Iterable

from pcapi import settings
from pcapi.connectors.googledrive import GoogleDriveBackend
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


def _get_password(row: dict) -> str:
    if row.get("Mot de passe"):  # Keep compatibility with CSV without this column
        return row["Mot de passe"]
    return settings.TEST_DEFAULT_PASSWORD


def _create_beneficiary(row: dict, role: UserRole | None) -> User:
    user = users_api.create_account(
        email=sanitize_email(row["Mail"]),
        password=_get_password(row),
        birthdate=_get_birth_date(row),
        is_email_validated=True,
        send_activation_mail=False,
        remote_updates=False,
    )
    if role == UserRole.BENEFICIARY:
        deposit = payments_api.create_deposit(user, "import_test_users (csv)", eligibility=EligibilityType.AGE18)
        repository.save(deposit)
        user.add_beneficiary_role()
    elif role == UserRole.UNDERAGE_BENEFICIARY:
        deposit = payments_api.create_deposit(
            user, "import_test_users (csv)", eligibility=EligibilityType.UNDERAGE, age_at_registration=16
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
            password=_get_password(row),
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

    user.validationToken = None
    user.isEmailValidated = True
    user.add_pro_role()

    return user


def _add_or_update_user_from_row(row: dict, update_if_exists: bool) -> User | None:
    user = find_user_by_email(row["Mail"])
    if user and not update_if_exists:
        return None

    if user:
        user.dateOfBirth = _get_birth_date(row)
        user.setPassword(_get_password(row))
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
    user.comment = row["Type"]
    user.add_test_role()
    repository.save(user)

    logger.info(
        "Created or updated user=%s <%s> %s from CSV import", user.id, user.email, [role.value for role in user.roles]
    )

    return user


def _add_or_update_admin(update_if_exists: bool) -> None:
    admin = find_user_by_email("admin@example.com")
    if admin and not update_if_exists:
        return
    if not admin:
        admin = users_api.create_account(
            email="admin@example.com",
            password=settings.TEST_DEFAULT_PASSWORD,
            birthdate=datetime(1946, 12, 24),
            is_email_validated=True,
            send_activation_mail=False,
            remote_updates=False,
        )
    admin.setPassword(settings.TEST_DEFAULT_PASSWORD)
    admin.remove_beneficiary_role()
    admin.add_admin_role()
    admin.firstName = "Jeanne"
    admin.lastName = "Admin"
    admin.publicName = f"{admin.firstName} {admin.lastName}"
    repository.save(admin)
    logger.info("Created or updated admin user=%s", admin.id)


def create_or_update_users(rows: Iterable[dict], update_if_exists: bool = False) -> list[User]:
    # The purpose of this function is to recreate test users on
    # staging after the staging database is reset. It's not meant to
    # be used anywhere else, and certainly not on production.
    if settings.IS_PROD:
        raise ValueError("This function is not supposed to be run on production")

    users = []
    for row in rows:
        user = _add_or_update_user_from_row(row, update_if_exists)
        if user:
            users.append(user)

    if settings.IS_STAGING or settings.IS_TESTING or settings.IS_RUNNING_TESTS:
        _add_or_update_admin(update_if_exists)

    return users


def create_users_from_csv(csv_file: TextIOWrapper, update_if_exists: bool = False) -> list[User]:
    csv_reader = csv.DictReader(csv_file)
    return create_or_update_users(csv_reader, update_if_exists=update_if_exists)


def create_users_from_google_sheet(document_id: str, update_if_exists: bool = False) -> list[User]:
    # Replace "/edit" with "/export?format=csv" in Google Drive URL to get CSV file
    backend = GoogleDriveBackend()
    content = backend.download_file(document_id, "text/csv")
    wrapper = TextIOWrapper(content, encoding="utf-8")
    return create_users_from_csv(wrapper, update_if_exists=update_if_exists)


if __name__ == "__main__":
    from pcapi.flask_app import app

    parser = argparse.ArgumentParser(description="""Creates or updates users listed in a Google Sheet or CSV file""")
    parser.add_argument("-f", "--filename", dest="filename", help="Path to the CSV file to import")
    parser.add_argument("-g", "--google", dest="google_id", help="Google document id")
    parser.add_argument(
        "-d",
        "--default",
        dest="default",
        help="Import from default Google document set in IMPORT_USERS_GOOGLE_DOCUMENT_ID",
        action="store_true",
        default=False,
    )
    parser.add_argument(
        "-u", "--update", dest="update", help="Update users which already exist", action="store_true", default=False
    )
    args = parser.parse_args()

    if len([param for param in (args.filename, args.google_id, args.default) if param]) != 1:
        raise ValueError("This script requires either the path to a CSV file or the id of Google document or default")

    with app.app_context():
        if args.filename:
            source = args.filename
            with open(source, encoding="utf-8") as fp:
                new_users = create_users_from_csv(fp)
        else:
            if args.google_id:
                source = args.google_id
            else:
                source = settings.IMPORT_USERS_GOOGLE_DOCUMENT_ID
                if not source:
                    raise ValueError("IMPORT_USERS_GOOGLE_DOCUMENT_ID is not configured")
            new_users = create_users_from_google_sheet(source, args.update)

    logger.info("Created or updated %d users from %s", len(new_users), source)
