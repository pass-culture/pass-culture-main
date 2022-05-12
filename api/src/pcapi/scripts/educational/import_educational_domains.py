import csv
import logging
from typing import Iterable

from pcapi.core.educational.models import EducationalDomain
from pcapi.models import db


logger = logging.getLogger(__name__)

DEFAULT_FILEPATH = "/tmp/"


def import_educational_domains(
    filename: str,
    path: str = DEFAULT_FILEPATH,
) -> None:
    if path is not None and path != DEFAULT_FILEPATH and not path.endswith("/"):
        path += "/"

    with open(f"{path}{filename}", "r", encoding="utf-8") as csv_file:
        csv_rows = csv.DictReader(csv_file, delimiter=";")
        headers = csv_rows.fieldnames
        if not headers or "name" not in headers:
            print("\033[91mERROR: name missing in CSV headers\033[0m")
            return
        _process_educational_csv(csv_rows)
    return


def _process_educational_csv(
    educational_domains_rows: Iterable[dict],
) -> None:
    for row in educational_domains_rows:
        name = row["name"]

        educational_domain = EducationalDomain(name=name)
        db.session.add(educational_domain)
        logger.info("Educational domain with name %s has been created", name)

    db.session.commit()
