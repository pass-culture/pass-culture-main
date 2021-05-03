import csv
import logging
from typing import Iterable

from pcapi.core.users.models import User
from pcapi.repository import repository


logger = logging.getLogger(__name__)


def process_catching_up_beneficiaries_addresses(iterable: Iterable[dict]) -> None:
    total = 0
    for row in iterable:
        user = User.query.get(row["beneficiary_id"])
        if user and user.isBeneficiary:
            total += 1
            user.address = row["user_address"]
            repository.save(user)
    print("Count: %d user's address imported" % total)


def _read_file(csv_file) -> None:
    csv_reader = csv.DictReader(csv_file)
    process_catching_up_beneficiaries_addresses(csv_reader)


def catching_up_dms_beneficiaries_adresses_from_csv_file(csv_file_path: str) -> None:
    logger.info("Import dms beneficiary addresses", extra={"csv_path": csv_file_path})
    with open(csv_file_path) as fp:
        _read_file(fp)
