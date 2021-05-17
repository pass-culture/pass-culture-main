import csv
import logging
from typing import Iterable

from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.repository import repository


logger = logging.getLogger(__name__)


def process_catching_up_beneficiaries_addresses(iterable: Iterable[dict]) -> None:
    users_ids = []
    user_address_by_ids = {}
    updated_users_count = 0

    for row in iterable:
        beneficiary_id = row["beneficiary_id"]
        beneficiary_address = row["user_address"]
        user_address_by_ids[beneficiary_id] = beneficiary_address
        users_ids.append(beneficiary_id)

    number_of_beneficiaries_to_update = len(users_ids)
    batch_size = 1000
    for current_start_index in range(0, number_of_beneficiaries_to_update, batch_size):
        users_ids_batch = users_ids[
            current_start_index : min(current_start_index + batch_size, number_of_beneficiaries_to_update)
        ]

        users_to_update = User.query.filter(User.id.in_(users_ids_batch), User.isBeneficiary.is_(True)).all()
        updated_users = []
        for user in users_to_update:
            user.address = user_address_by_ids[str(user.id)]
            updated_users.append(user)

        repository.save(*updated_users)
        db.session.commit()

        updated_users_count += len(updated_users)

    logger.info("Import finished", extra={"users_to_update": len(users_ids), "users_updated": updated_users_count})


def _read_file(csv_file) -> None:
    csv_reader = csv.DictReader(csv_file)
    process_catching_up_beneficiaries_addresses(csv_reader)


def catching_up_dms_beneficiaries_adresses_from_csv_file(csv_file_path: str) -> None:
    logger.info("Import DMS beneficiary addresses", extra={"csv_path": csv_file_path})
    with open(csv_file_path) as fp:
        _read_file(fp)
