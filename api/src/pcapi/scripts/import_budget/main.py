import argparse
import logging
import os

from pcapi.app import app
from pcapi.core.educational import commands
from pcapi.core.educational import models as educational_models


# from pcapi.models import db


logger = logging.getLogger(__name__)

app.app_context().push()

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
    path = f"{namespace_dir}/{args.filename}"

    run_args = [
        "--path",
        path,
        "--year",
        str(args.year),
        "--ministry",
        args.ministry,
        "--conflict",
        args.conflict,
        # "--dry-run",
        # str(not args.not_dry),
    ]
    if args.final:
        run_args.append("--final")

    logger.info("Calling import_deposit_csv command with args %s", run_args)
    # runner = app.test_cli_runner()
    # runner.invoke(commands.import_deposit_csv, run_args, catch_exceptions=False)
    commands.import_deposit_csv.main(args=run_args, standalone_mode=False)

    logger.info("Finished import budget")
    # if args.not_dry:
    #     logger.info("Finished import budget")
    # else:
    #     logger.info("Finished dry run for import budget, rollback")
    #     db.session.rollback()
