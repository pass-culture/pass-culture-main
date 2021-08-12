# isort: skip_file
import csv
from datetime import datetime
import sys
from typing import Iterable


import pcapi.models  # pylint: disable=unused-import
from pcapi import settings
import pcapi.core.payments.api as payments_api
import pcapi.core.users.api as users_api
from pcapi.core.users.models import User
from pcapi.core.users.utils import sanitize_email
from pcapi.repository import repository
from pcapi.repository.user_queries import find_user_by_email
import logging

logger = logging.getLogger(__name__)


def create_or_update_users(rows: Iterable[dict]) -> list[User]:
    # The purpose of this function is to recreate test users on
    # staging after the staging database is reset. It's not meant to
    # be used anywhere else, and certainly not on production.
    if settings.IS_PROD:
        raise ValueError("This function is not supposed to be run on production")

    users = []
    for row in rows:
        user = find_user_by_email(row["Mail"])
        birthdate = datetime.strptime(row["Date de naissance"], "%Y-%m-%d")
        if user:
            user.dateOfBirth = birthdate
            user.setPassword(settings.STAGING_TEST_USER_PASSWORD)
        else:
            user = users_api.create_account(
                email=sanitize_email(row["Mail"]),
                password=settings.STAGING_TEST_USER_PASSWORD,
                birthdate=birthdate,
                is_email_validated=True,
                send_activation_mail=False,
                remote_updates=False,
            )
            deposit = payments_api.create_deposit(user, "import_users (csv)")
            repository.save(deposit)

        user.add_beneficiary_role()
        user.lastName = row["Nom"]
        user.firstName = row["Prénom"]
        user.publicName = f"{user.firstName} {user.lastName}"
        user.phoneNumber = row["Téléphone"]
        user.departementCode = row["Département"]
        user.postalCode = row["Code postal"]
        repository.save(user)

        users.append(user)
        logger.info("Created or updated user=%s from CSV import", user.id)

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
    admin.publicName = f"{user.firstName} {user.lastName}"
    repository.save(admin)
    logger.info("Created or updated admin user=%s", admin.id)
    return users


def _read_file(csv_file):
    csv_reader = csv.DictReader(csv_file)
    return create_or_update_users(csv_reader)


if __name__ == "__main__":
    from pcapi.app import app

    if len(sys.argv) != 2:
        raise ValueError("This script requires one argument: the path to the CSV file with users to import")
    csv_file_path = sys.argv[1]
    with open(csv_file_path) as fp:
        with app.app_context():
            new_users = _read_file(fp)
    logger.info("Created or updated %d beneficiary users from %s", len(new_users), csv_file_path)
