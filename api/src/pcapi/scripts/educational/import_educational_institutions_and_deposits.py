import csv
from datetime import datetime
import logging
import pathlib
from typing import Iterable

from pcapi.core.educational import api
from pcapi.core.educational import exceptions
from pcapi.core.educational import repository as educational_repository
from pcapi.core.educational.models import Ministry


logger = logging.getLogger(__name__)

DEFAULT_FILEPATH = "/tmp/"


def import_educational_institutions_and_deposits(
    filename: str,
    ministry: Ministry,
    path: str = DEFAULT_FILEPATH,
    educational_year_beginning: int | None = None,
) -> None:
    if path is not None and path != DEFAULT_FILEPATH and not path.endswith("/"):
        path += "/"

    with open(f"{path}{filename}", "r", encoding="utf-8") as csv_file:
        csv_rows = csv.DictReader(csv_file, delimiter=";")
        headers = csv_rows.fieldnames
        header_names = set(["UAICode", "name", "city", "postalCode", "phoneNumber", "email", "depositAmount"])
        if not headers or not header_names.issubset(set(headers)):
            header_names_list_string = ", ".join(header_names)
            print(
                f"\033[91mERROR: CSV headers is missing at least one of the following header : {header_names_list_string} \033[0m"
            )
            return
        _process_educational_csv(csv_rows, ministry, educational_year_beginning)
    return


def _process_educational_csv(
    educational_institutions_rows: Iterable[dict],
    ministry: Ministry,
    educational_year_beginning: int | None = None,
) -> None:
    current_year = educational_year_beginning if educational_year_beginning is not None else datetime.utcnow().year
    try:
        educational_year = educational_repository.get_educational_year_beginning_at_given_year(current_year)
    except exceptions.EducationalYearNotFound:
        print("\033[91mERROR: script has ceased execution")
        print(
            "Please add educational years in database as no educational year has been found beginning at current year\033[0m"
        )
        return

    for row in educational_institutions_rows:
        institution_id = row["UAICode"]
        deposit_amount = row["depositAmount"]
        institution_data = {
            "name": row["name"],
            "city": row["city"],
            "postalCode": row["postalCode"],
            "phoneNumber": row["phoneNumber"],
            "email": row["email"],
        }

        educational_institution = educational_repository.find_educational_institution_by_uai_code(institution_id)
        if educational_institution is None:
            educational_institution = api.create_educational_institution(institution_id, institution_data)
            logger.info("Educational institution with UAI code %s has been created", institution_id)

        if educational_repository.find_educational_deposit_by_institution_id_and_year(
            educational_institution.id, educational_year.adageId
        ):
            print(
                f"\033[93mWARNING: deposit for educational institution with id {educational_institution.institutionId} already exists\033[0m"
            )
            continue
        educational_deposit = api.create_educational_deposit(
            educational_year.adageId, educational_institution.id, deposit_amount, ministry
        )
        logger.info(
            "Educational deposit has been created",
            extra={
                "educational_deposit_id": educational_deposit.id,
                "script": "import_educational_institutions_and_deposits",
                "amount": str(educational_deposit.amount),
                "uai_code": institution_id,
                "year_id": educational_year.id,
                "ministry": ministry,
            },
        )


def merge_budget_and_data_csv(
    budgets_csv_filename: str, data_csv_filename: str, path: str = DEFAULT_FILEPATH
) -> pathlib.Path:
    if path is not None and path != DEFAULT_FILEPATH and not path.endswith("/"):
        path += "/"

    budget_by_uai = {}
    rows = []

    with open(f"./{budgets_csv_filename}", "r", encoding="utf-8") as budgets_file:
        budgets_rows = csv.DictReader(budgets_file, delimiter=";")
        for row in budgets_rows:
            budget_by_uai[row["UAICode"]] = row["budget"]

    with open(f"./{data_csv_filename}", "r", encoding="utf-8") as data_file:
        data_row = csv.DictReader(data_file, delimiter=";")
        for row in data_row:
            rows.append(
                (
                    row["UAICode"],
                    budget_by_uai[row["UAICode"]],
                    row["city"],
                    row["postalCode"],
                    row["email"],
                    row["phoneNumber"],
                    row["name"],
                )
            )

    header = ["UAICode", "depositAmount", "city", "postalCode", "email", "phoneNumber", "name"]
    csv_path: pathlib.Path = pathlib.Path() / "budgets.csv"

    with open(csv_path, "w+", encoding="utf-8") as fp:
        writer = csv.writer(fp, quoting=csv.QUOTE_NONNUMERIC, delimiter=";")
        writer.writerow(header)
        writer.writerows(row for row in rows)

    return csv_path
