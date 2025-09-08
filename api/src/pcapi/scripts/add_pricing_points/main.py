"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/ogeber/pc-37715-add-missing-pricing-points/api/src/pcapi/scripts/add_pricing_points/main.py

"""

import argparse
import csv
import logging
import os
import typing

from sqlalchemy import exc as sa_exc

from pcapi.app import app
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers.api import link_venue_to_pricing_point
from pcapi.core.offerers.exceptions import CannotLinkVenueToPricingPoint
from pcapi.models import api_errors, db
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)

VENUE_ID_HEADER = "venue_id"
SIRET_VENUE_ID_HEADER = "siret_venue_id"


def _read_csv_file(filename: str) -> typing.Iterator[dict[str, str]]:
    namespace_dir = os.path.dirname(os.path.abspath(__file__))
    with open(f"{namespace_dir}/{filename}.csv", "r", encoding="utf-8") as csv_file:
        csv_rows = csv.DictReader(csv_file, delimiter=",")
        yield from csv_rows


def _get_venues_to_update(filename: str) -> dict[int, list[offerers_models.Venue]]:
    rows = list(_read_csv_file(filename))

    venue_ids = {row[VENUE_ID_HEADER] for row in rows}
    venues_dict = {
        venue.id: venue
        for venue in db.session.query(offerers_models.Venue).filter(offerers_models.Venue.id.in_(venue_ids)).all()
    }

    result: dict[int, list[offerers_models.Venue]] = {}
    for row in rows:
        venue_id = int(row[VENUE_ID_HEADER])
        siret_id = int(row[SIRET_VENUE_ID_HEADER])
        if venue_id in venues_dict:
            if siret_id not in result:
                result[siret_id] = []
            result[siret_id].append(venues_dict[venue_id])
        else:
            logger.info("Venue %s not found, not processing", venue_id)
    return result


@atomic()
def main(dry_run: bool = True) -> None:
    if dry_run:
        mark_transaction_as_invalid()
    venues_to_update_dict = _get_venues_to_update("venues_without_pricing_point")

    for venue_with_siret_id, venues_to_update in venues_to_update_dict.items():
        for venue_to_update in venues_to_update:
            if venue_to_update.current_pricing_point_id == venue_with_siret_id:
                continue
            with atomic():
                try:
                    link_venue_to_pricing_point(venue_to_update, pricing_point_id=venue_with_siret_id)
                except (CannotLinkVenueToPricingPoint, sa_exc.OperationalError, api_errors.ApiErrors):
                    logger.error(
                        "ERROR: Could not link venue %s to pricing point %s", venue_to_update.id, venue_with_siret_id
                    )
                    mark_transaction_as_invalid()
                    continue


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()
    dry_run = not args.not_dry

    main(dry_run=dry_run)

    if dry_run:
        logger.info("Finished dry run")
    else:
        logger.info("Finished")
