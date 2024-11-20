import argparse
import csv
from decimal import Decimal
import logging
import os

from pcapi.app import app
from pcapi.core.educational import exceptions as educational_exceptions
from pcapi.core.educational import models as educational_models
from pcapi.core.educational import repository as educational_repository
from pcapi.core.educational.api import institution as institution_api


logger = logging.getLogger(__name__)

app.app_context().push()


def import_deposit_csv(*, path: str, year: int, ministry: str, conflict: str, final: bool) -> None:
    """
    import CSV deposits and update institution according to adage data.

    CSV format change every time we try to work with it.
    """
    if not os.path.exists(path):
        print("\033[91mERROR: The given file does not exists.\033[0m")
        return

    try:
        educational_year = educational_repository.get_educational_year_beginning_at_given_year(year)
    except educational_exceptions.EducationalYearNotFound:
        # print(f"\033[91mERROR: Educational year not found for year {year}.\033[0m")
        logger.info("Educational year not found for year")
        return
    with open(path, "r", encoding="utf-8") as csv_file:
        csv_rows = csv.DictReader(csv_file, delimiter=";")
        headers = csv_rows.fieldnames
        if not headers or ("UAICode" not in headers and "UAI" not in headers):
            # print("\033[91mERROR: UAICode or depositAmount missing in CSV headers\033[0m")
            logger.info("UAICode or depositAmount missing in CSV headers")
            return
        data: dict[str, Decimal] = {}
        # sometimes we get 1 row per institution and sometimes 1 row per class.
        for row in csv_rows:
            # try to get the UAI
            uai_header = "UAI" if "UAI" in headers else "UAICode"
            uai = row[uai_header].strip()
            # try to get the amount
            if "Crédits de dépenses" in headers or "depositAmount" in headers:
                amount_header = "depositAmount" if "depositAmount" in headers else "Crédits de dépenses"
                amount = Decimal(row[amount_header])
            elif "montant par élève" in headers and "Effectif" in headers:
                amount = Decimal(row["Effectif"]) * Decimal(row["montant par élève"])
            else:
                # print("\033[91mERROR: Now way to get the amount found\033[0m")
                logger.info("Now way to get the amount found")
                return

            if uai in data:
                data[uai] += amount
            else:
                data[uai] = amount

        logger.info("Finished reading CSV, starting import deposit")
        institution_api.import_deposit_institution_data(
            data=data,
            educational_year=educational_year,
            ministry=educational_models.Ministry[ministry],
            conflict=conflict,
            final=final,
        )


if __name__ == "__main__":
    # see import_deposit_csv command for argument descriptions
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--ministry", type=str, choices=[m.name for m in educational_models.Ministry], required=True)
    parser.add_argument("--filename", type=str, required=True)
    parser.add_argument("--conflict", type=str, choices=["keep", "replace"], required=True, default="keep")
    parser.add_argument("--final", action="store_true")
    # parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    namespace_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = f"{namespace_dir}/{args.filename}"

    logger.info("Calling import_deposit_csv with args %s", args)
    import_deposit_csv(
        path=file_path,
        year=args.year,
        ministry=args.ministry,
        conflict=args.conflict,
        final=args.final,
    )
    logger.info("Finished import budget")

    # run_args = [
    #     "--path",
    #     path,
    #     "--year",
    #     str(args.year),
    #     "--ministry",
    #     args.ministry,
    #     "--conflict",
    #     args.conflict,
    #     # "--dry-run",
    #     # str(not args.not_dry),
    # ]
    # if args.final:
    #     run_args.append("--final")

    # logger.info("Calling import_deposit_csv command with args %s", run_args)
    # runner = app.test_cli_runner()
    # runner.invoke(commands.import_deposit_csv, run_args, catch_exceptions=False)

    # if args.not_dry:
    #     logger.info("Finished import budget")
    # else:
    #     logger.info("Finished dry run for import budget, rollback")
    #     db.session.rollback()
