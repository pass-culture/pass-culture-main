import csv
from datetime import datetime
import logging
from typing import Iterable

from pcapi.core.educational import api
from pcapi.core.educational import exceptions
from pcapi.core.educational import repository as educational_repository


logger = logging.getLogger(__name__)

DEFAULT_FILEPATH = ""


def import_educational_institutions_and_deposits(filename: str, path: str = DEFAULT_FILEPATH) -> None:
    if path is not None and path != DEFAULT_FILEPATH and not path.endswith("/"):
        path += "/"

    with open(f"{path}{filename}", "r") as csv_file:
        csv_rows = csv.DictReader(csv_file, delimiter=";")
        headers = csv_rows.fieldnames
        if not headers or "UAICode" not in headers or "depositAmount" not in headers:
            print("\033[91mERROR: UAICode or depositAmount missing in CSV headers\033[0m")
            return
        _process_educational_csv(csv_rows)
    return


def _process_educational_csv(educational_institutions_rows: Iterable[dict]) -> None:
    currentYear = datetime.now().year
    try:
        educational_year = educational_repository.get_educational_year_beginning_at_given_year(currentYear)
    except exceptions.EducationalYearNotFound:
        print("\033[91mERROR: script has ceased execution")
        print(
            "Please add educational years in database as no educational year has been found beginning at current year\033[0m"
        )
        return

    for row in educational_institutions_rows:
        institution_id = row["UAICode"]
        deposit_amount = row["depositAmount"]

        educational_institution = educational_repository.find_educational_institution_by_uai_code(institution_id)
        if educational_institution is None:
            educational_institution = api.create_educational_institution(institution_id)
            logger.info("Educational institution with UAI code %s has been created", institution_id)

        if educational_repository.find_educational_deposit_by_institution_id_and_year(
            educational_institution.id, educational_year.adageId
        ):
            print(
                f"\033[93mWARNING: deposit for educational institution with id {educational_institution.institutionId} already exists\033[0m"
            )
            continue

        educational_deposit = api.create_educational_deposit(
            educational_year.adageId, educational_institution.id, deposit_amount
        )
        logger.info(
            "Educational deposit has been created",
            extra={
                "educational_deposit_id": educational_deposit.id,
                "script": "import_educational_institutions_and_deposits",
                "amount": str(educational_deposit.amount),
                "uai_code": institution_id,
                "year_id": educational_year.id,
            },
        )
