import argparse
import csv
import decimal
import logging
import os

from pcapi.app import app
from pcapi.core.educational import exceptions as educational_exceptions
from pcapi.core.educational import models as educational_models
from pcapi.core.educational import repository as educational_repository
from pcapi.models import db
from pcapi.settings import IS_INTEGRATION


logger = logging.getLogger(__name__)

app.app_context().push()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--year",
        type=int,
        required=True,
        help="Year of start of the edcational year (example: 2023 for educational year 2023-2024).",
    )
    parser.add_argument(
        "--ministry",
        type=str,
        choices=[m.name for m in educational_models.Ministry],
        required=True,
        help="Ministry for this deposit.",
    )
    parser.add_argument("--filename", type=str, required=True, help="Name of the CSV to import.")
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    if not IS_INTEGRATION:
        raise RuntimeError("This should run in integration only")

    namespace_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = f"{namespace_dir}/{args.filename}"

    if not os.path.exists(file_path):
        raise ValueError("The given file does not exist")

    # extract amount by uai from csv
    with open(file_path, "r", encoding="utf-8") as csv_file:
        csv_rows = csv.DictReader(csv_file, delimiter=";")
        headers = csv_rows.fieldnames
        if not headers or ("UAICode" not in headers and "UAI" not in headers):
            raise ValueError("UAICode or depositAmount missing in CSV headers")

        data: dict[str, decimal.Decimal] = {}
        # sometimes we get 1 row per institution and sometimes 1 row per class.
        for row in csv_rows:
            # try to get the UAI
            uai_header = "UAI" if "UAI" in headers else "UAICode"
            uai = row[uai_header].strip()
            # try to get the amount
            if "Crédits de dépenses" in headers or "depositAmount" in headers:
                amount_header = "depositAmount" if "depositAmount" in headers else "Crédits de dépenses"
                amount = decimal.Decimal(row[amount_header])
            elif "montant par élève" in headers and "Effectif" in headers:
                amount = decimal.Decimal(row["Effectif"]) * decimal.Decimal(row["montant par élève"])
            else:
                raise ValueError("Now way to get the amount found")

            if uai in data:
                data[uai] += amount
            else:
                data[uai] = amount

    # get educational year
    try:
        educational_year = educational_repository.get_educational_year_beginning_at_given_year(args.year)
    except educational_exceptions.EducationalYearNotFound:
        raise ValueError(f"Educational year not found for year {args.year}")

    # create or update deposits
    institution_by_uai = {
        institution.institutionId: institution for institution in educational_models.EducationalInstitution.query
    }
    for uai, amount in data.items():
        db_institution = institution_by_uai.get(uai)
        if db_institution is None:
            continue

        deposit = educational_models.EducationalDeposit.query.filter(
            educational_models.EducationalDeposit.educationalYear == educational_year,
            educational_models.EducationalDeposit.educationalInstitution == db_institution,
        ).one_or_none()

        if deposit is not None:
            deposit.ministry = args.ministry
            deposit.amount = amount
            deposit.isFinal = False
        else:
            deposit = educational_models.EducationalDeposit(
                educationalYear=educational_year,
                educationalInstitution=db_institution,
                amount=amount,
                ministry=args.ministry,
                isFinal=False,
            )
        db.session.add(deposit)

    if args.not_dry:
        logger.info("Finished import budget, committing")
        db.session.commit()
    else:
        logger.info("Finished dry run for import budget, rollback")
        db.session.rollback()
