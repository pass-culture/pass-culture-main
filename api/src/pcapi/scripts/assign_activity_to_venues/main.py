"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=master \
  -f NAMESPACE=assign_activity_to_venues \
  -f SCRIPT_ARGUMENTS="--activity=MUSEUM --domain=1 --domain=13";

"""

import argparse
import csv
import logging
import os
import typing

from pcapi.app import app
from pcapi.core.educational.models import EducationalDomain
from pcapi.core.offerers.models import Activity
from pcapi.core.offerers.models import Venue
from pcapi.models import db


logger = logging.getLogger(__name__)


FILENAME = "venues.csv"
HEADER = "Venue ID"


def _read_input_file() -> typing.Iterator[dict[str, str]]:
    namespace_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        with open(f"{namespace_dir}/{FILENAME}", "r", encoding="utf-8") as csv_file:
            csv_rows = csv.DictReader(csv_file, delimiter=",")
            yield from csv_rows
    except Exception:  # pylint: disable=broad-except
        logger.warning("Use input file %s", FILENAME)
        return


def main(open_to_public: bool, activity: Activity | None, domains: set[EducationalDomain] | None) -> None:

    venue_ids = {int(row[HEADER]) for row in _read_input_file()}
    venues = db.session.query(Venue).where(Venue.id.in_((venue_ids))).all()

    for venue in venues:
        if open_to_public is not None:
            venue.isOpenToPublic = open_to_public
        if activity:
            venue.activity = activity
        if domains:
            venue_domains = domains.copy()
            venue_domains.update(venue.collectiveDomains)
            venue.collectiveDomains = list(venue_domains)
        db.session.add(venue)

    logger.info(
        "Setting isOpenToPublic %s, setting activity %s, adding domains %s for %i Venues. Updated ids: %s",
        open_to_public if open_to_public else "-",
        activity.name if activity else "-",
        [domain.name for domain in domains] if domains else "-",
        len(venue_ids),
        venue_ids if len(venue_ids) > 0 else "-",
    )


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--openToPublic", type=bool, help="open_to_public value - will not change if no value given")
    parser.add_argument("--activity", type=str, help="activity to set")
    parser.add_argument("--domain", action="append", type=int, help="domain(s) to set")
    args = parser.parse_args()

    activity_arg: Activity | None = None
    if args.activity:
        try:
            activity_arg = Activity[args.activity]
        except KeyError as exception:
            raise ValueError("Use a correct activity value in --activity argument") from exception

    domains_arg: set[EducationalDomain] | None = None
    if args.domain:
        domains_arg = set(db.session.query(EducationalDomain).where(EducationalDomain.id.in_(args.domain)).all())
        if set(args.domain) - {domain.id for domain in domains_arg}:
            raise ValueError("Use correct educational domain id in --domain argument")

    main(
        open_to_public=args.openToPublic,
        activity=activity_arg,
        domains=domains_arg,
    )

    if args.apply:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
