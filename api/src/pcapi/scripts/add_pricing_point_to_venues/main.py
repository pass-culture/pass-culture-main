"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=pcharlet/pc-38814-script-add-pricing-point \
  -f NAMESPACE=add_pricing_point_to_venues \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import csv
import logging
import os
import traceback
import typing

from pcapi.app import app
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)

VENUE_ID_HEADER = "venue_id"


def _read_csv_file() -> typing.Iterator[dict[str, str]]:
    namespace_dir = os.path.dirname(os.path.abspath(__file__))
    with open(f"{namespace_dir}/venues_without_pp.csv", "r", encoding="utf-8") as csv_file:
        csv_rows = csv.DictReader(csv_file, delimiter=",")
        yield from csv_rows


def _add_pp_to_venue(venue: offerers_models.Venue) -> None:
    new_pp_id = (
        db.session.query(offerers_models.Venue)
        .filter(
            offerers_models.Venue.managingOffererId == venue.managingOffererId, offerers_models.Venue.siret.is_not(None)
        )
        .one()
    ).current_pricing_point_id
    assert new_pp_id
    offerers_api.link_venue_to_pricing_point(venue, new_pp_id, force_link=True)


@atomic()
def main(not_dry: bool) -> None:
    if not not_dry:
        logger.info("Dry run mode enabled, no changes will be made to the database")
        mark_transaction_as_invalid()
    rows = list(_read_csv_file())
    for row in rows:
        venue = db.session.query(offerers_models.Venue).filter(offerers_models.Venue.id == row[VENUE_ID_HEADER]).one()
        try:
            with atomic():
                _add_pp_to_venue(venue)
        except Exception:
            print(traceback.format_exc())


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    main(not_dry=args.not_dry)

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
