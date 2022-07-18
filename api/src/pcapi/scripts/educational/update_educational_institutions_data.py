import csv
import logging
from typing import Iterable

from pcapi.core.educational import api
from pcapi.core.educational import repository as educational_repository
from pcapi.core.educational import utils
from pcapi.models import db


logger = logging.getLogger(__name__)

DEFAULT_FILEPATH = "/tmp/"


def import_educational_institutions_data(filename: str, path: str = DEFAULT_FILEPATH) -> None:
    if path is not None and path != DEFAULT_FILEPATH and not path.endswith("/"):
        path += "/"

    with open(f"{path}{filename}", "r", encoding="utf-8") as csv_file:
        csv_rows = csv.DictReader(csv_file, delimiter=";")
        headers = csv_rows.fieldnames
        header_names = set(["UAICode", "name", "city", "postalCode", "phoneNumber", "email"])
        if not headers or not header_names.issubset(set(headers)):
            header_names_list_string = ", ".join(header_names)
            print(
                f"\033[91mERROR: CSV headers is missing at least one of the following header : {header_names_list_string} \033[0m"
            )
            return
        _process_educational_csv(csv_rows)
    return


def _process_educational_csv(educational_institutions_rows: Iterable[dict]) -> None:
    nb_rows_to_save = 0
    educational_institutions = educational_repository.find_all_educational_institution()
    educational_institutions_key_by_id = {
        educational_institution.institutionId: educational_institution
        for educational_institution in educational_institutions
    }

    for row in educational_institutions_rows:
        institution_id = row["UAICode"]
        institution_type, institution_name = utils.get_institution_type_and_name(row["name"])
        institution_data = {
            "name": institution_name,
            "institutionType": institution_type,
            "city": row["city"],
            "postalCode": row["postalCode"],
            "phoneNumber": row["phoneNumber"],
            "email": row["email"],
        }

        educational_institution = educational_institutions_key_by_id.get(institution_id)

        if educational_institution is None:
            print(f"\033[91mEducational institution with id {institution_id} has not been found.\033[0m")

        if educational_institution is not None:
            educational_institution = api.update_educational_institution_data(institution_id, institution_data)

            db.session.add(educational_institution)
            nb_rows_to_save = nb_rows_to_save + 1

            if nb_rows_to_save % 1000 == 0:
                db.session.flush()

    db.session.commit()

    logger.info(
        "Educational institutions have been updated",
        extra={
            "script": "import_educational_institutions_data",
        },
    )
