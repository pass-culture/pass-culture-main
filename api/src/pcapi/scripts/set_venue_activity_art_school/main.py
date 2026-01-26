"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml   -f ENVIRONMENT=testing   -f BRANCH_NAME=bdalbianco/PC-38127_venueActivity_specific_cases   -f NAMESPACE=set_venue_activity_art_school   -f SCRIPT_ARGUMENTS="";

"""

import argparse
import csv
import logging
import os
import typing

from sqlalchemy import update

from pcapi.app import app
from pcapi.core.offerers.models import Activity
from pcapi.core.offerers.models import Venue
from pcapi.models import db


logger = logging.getLogger(__name__)

FILENAME = "venue_activity_art_school.csv"
HEADER = "Venue ID"
ACTIVITY = Activity.ART_SCHOOL


def read_csv_file() -> typing.Iterator[dict[str, str]]:
    namespace_dir = os.path.dirname(os.path.abspath(__file__))
    with open(f"{namespace_dir}/{FILENAME}", "r", encoding="utf-8") as csv_file:
        csv_rows = csv.DictReader(csv_file, delimiter=",")
        yield from csv_rows


def process_file(file_rows: typing.Iterator[dict[str, str]]) -> None:
    venue_ids = {int(row[HEADER]) for row in file_rows}
    result = db.session.execute(update(Venue).where(Venue.id.in_((venue_ids))).values(activity=ACTIVITY))
    logger.info(
        "Set venue.activity to ART_SCHOOL: %i Venues updated out of %i Venues to update",
        result.rowcount,  # type: ignore[attr-defined]
        len(venue_ids),
    )


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    process_file(read_csv_file())

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
