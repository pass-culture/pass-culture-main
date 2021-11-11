import csv
import logging
from typing import Iterable

from pcapi.core.users.models import User
from pcapi.repository import repository


logger = logging.getLogger(__name__)


def _update_beneficiaries_addresses(iterable: Iterable[dict]) -> None:
    beneficiaries_emails = []
    user_address_by_emails = {}
    updated_beneficiaries_count = 0

    for row in iterable:
        beneficiary_email = row["email"]
        beneficiary_address = row["adresse"]
        user_address_by_emails[beneficiary_email] = beneficiary_address
        beneficiaries_emails.append(beneficiary_email)

    number_of_beneficiaries_to_update = len(beneficiaries_emails)
    batch_size = 1000
    for current_start_index in range(0, number_of_beneficiaries_to_update, batch_size):
        beneficiaries_emails_batch = beneficiaries_emails[
            current_start_index : min(current_start_index + batch_size, number_of_beneficiaries_to_update)
        ]

        beneficiaries_to_update = User.query.filter(
            User.email.in_(beneficiaries_emails_batch), User.is_beneficiary.is_(True)
        ).all()
        updated_beneficiaries = []
        for beneficiary in beneficiaries_to_update:
            beneficiary.address = user_address_by_emails[beneficiary.email]
            updated_beneficiaries.append(beneficiary)

        repository.save(*updated_beneficiaries)
        updated_beneficiaries_count += len(updated_beneficiaries)

    logger.info(
        "Import finished",
        extra={"users_to_update": len(beneficiaries_emails), "users_updated": updated_beneficiaries_count},
    )


def _process_file(csv_file) -> None:
    csv_reader = csv.DictReader(csv_file)
    _update_beneficiaries_addresses(csv_reader)


def catching_up_dms_beneficiaries_adresses_from_csv_file(csv_file_path: str) -> None:
    logger.info("Import DMS beneficiary addresses", extra={"csv_path": csv_file_path})
    with open(csv_file_path) as fp:
        _process_file(fp)
