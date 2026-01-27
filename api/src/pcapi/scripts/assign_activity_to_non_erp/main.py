"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=master \
  -f NAMESPACE=assign_activity_to_non_erp \
  -f SCRIPT_ARGUMENTS="--activity=FESTIVAL";

"""

import argparse
import csv
import logging
import os
import typing

from sqlalchemy import select
from sqlalchemy import update

from pcapi.app import app
from pcapi.core.offerers.models import Activity
from pcapi.core.offerers.models import Venue
from pcapi.core.offerers.schemas import VenueTypeCode
from pcapi.models import db


logger = logging.getLogger(__name__)


FILENAME = "venues.csv"
HEADER = "Venue ID"
ACTIVITY_MAPPING = {
    Activity.FESTIVAL.name: [VenueTypeCode.FESTIVAL],
    Activity.TRAVELLING_CINEMA.name: [VenueTypeCode.TRAVELING_CINEMA],
    Activity.ARTS_EDUCATION.name: [VenueTypeCode.ARTISTIC_COURSE],
    Activity.CULTURAL_MEDIATION.name: [
        VenueTypeCode.VISUAL_ARTS,
        VenueTypeCode.CULTURAL_CENTRE,
        VenueTypeCode.LIBRARY,
        VenueTypeCode.BOOKSTORE,
        VenueTypeCode.MUSEUM,
    ],
}


def _read_input_file() -> typing.Iterator[dict[str, str]]:
    namespace_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        with open(f"{namespace_dir}/{FILENAME}", "r", encoding="utf-8") as csv_file:
            csv_rows = csv.DictReader(csv_file, delimiter=",")
            yield from csv_rows
    except Exception:  # pylint: disable=broad-except
        logger.warning("Use input file %s or --apply-to-all argument", FILENAME)
        return


def _find_venues_to_migrate(activity: Activity) -> set[int]:
    venue_ids = db.session.scalars(
        select(Venue.id).filter(
            Venue.isOpenToPublic.is_(False),
            Venue.venueTypeCode.in_(ACTIVITY_MAPPING[activity.name]),
        )
    ).all()
    return set(venue_ids)


def main(activity_arg: str | None, apply_to_all: bool = False) -> None:
    if not activity_arg:
        logger.warning(
            "Use --activity argument",
        )
        return

    try:
        activity = Activity[activity_arg]
    except KeyError:
        logger.warning(
            "Use --activity argument and spell it correctly",
        )
        return

    if not apply_to_all:
        venue_ids = {int(row[HEADER]) for row in _read_input_file()}
    else:
        venue_ids = _find_venues_to_migrate(activity)

    result = db.session.execute(update(Venue).where(Venue.id.in_((venue_ids))).values(activity=activity))
    logger.info(
        "Setting activity to %s: %i Venues updated out of %i Venues to update",
        activity.name,
        result.rowcount,  # type: ignore[attr-defined]
        len(venue_ids),
    )


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    parser.add_argument("--activity", type=str, help="activity to set")
    # explicit arg to avoid running the script for all structures if file input is forgotten
    parser.add_argument("--apply-to-all", action="store_true")
    args = parser.parse_args()

    main(
        activity_arg=args.activity,
        apply_to_all=args.apply_to_all,
    )

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
