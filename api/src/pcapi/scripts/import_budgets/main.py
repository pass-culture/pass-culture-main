import argparse
import logging
import os

from pcapi.app import app
from pcapi.core.educational import models as educational_models
from pcapi.core.educational.api.institution import import_deposit_institution_csv
from pcapi.models import db


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
    parser.add_argument(
        "--conflict", type=str, choices=["keep", "replace"], default="keep", help="Overide previous ministry if needed."
    )
    parser.add_argument(
        "--educational-program-name",
        type=str,
        choices=[educational_models.PROGRAM_MARSEILLE_EN_GRAND],
        help="Link the institutions to a program, if given.",
    )
    parser.add_argument("--final", action="store_true", help="Flag deposits as final.")
    parser.add_argument("--not-dry", action="store_true", help="Commit the changes.")
    args = parser.parse_args()

    namespace_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = f"{namespace_dir}/{args.filename}"

    logger.info("Calling import_deposit_institution_csv with args %s", args)
    total_amount = import_deposit_institution_csv(
        path=file_path,
        year=args.year,
        ministry=args.ministry,
        conflict=args.conflict,
        final=args.final,
        program_name=args.educational_program_name,
    )

    with open(f"{os.environ.get('OUTPUT_DIRECTORY')}/total_amount.txt", "w", encoding="utf8") as f:
        f.write(f"Total imported amount: {total_amount}")

    if args.not_dry:
        logger.info("Finished import budget, committing")
        db.session.commit()
    else:
        logger.info("Finished dry run for import budget, rollback")
        db.session.rollback()
