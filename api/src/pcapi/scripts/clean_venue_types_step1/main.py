import argparse
import csv
import logging
import os
import typing

import pcapi.core.offerers.models as offerers_models
import pcapi.core.offerers.schemas as offerers_schemas
from pcapi.models import db


logger = logging.getLogger(__name__)

NEW_VENUE_TYPE_HEADER = "NEW VENUE TYPE"
VENUE_ID_HEADER = "venue_id"
VENUE_TYPE_CODE_MAPPING = {v.value: v.name for v in offerers_schemas.VenueTypeCode}


def read_csv_file() -> typing.Iterator[dict[str, str]]:
    namespace_dir = os.path.dirname(os.path.abspath(__file__))
    with open(f"{namespace_dir}/venues_types_to_change.csv", "r", encoding="utf-8") as csv_file:
        csv_rows = csv.DictReader(csv_file, delimiter=",")
        yield from csv_rows


def process_file(rows: typing.Iterator[dict[str, str]]) -> None:
    data: dict[str, list[str]] = {}
    for row in rows:
        try:
            venue_type_code = row[NEW_VENUE_TYPE_HEADER]
            venue_type_code = venue_type_code.strip("\n")
            data.setdefault(VENUE_TYPE_CODE_MAPPING[venue_type_code], []).append(row[VENUE_ID_HEADER])
        except KeyError:
            print("'%s' is not a valid value" % venue_type_code)
    for venue_type_code, ids in data.items():
        offerers_models.Venue.query.filter(offerers_models.Venue.id.in_(ids)).update(
            {offerers_models.Venue.venueTypeCode: venue_type_code}, synchronize_session=False
        )
        logger.info("Updating venue type to '%s' for ids=%s", venue_type_code, str(ids))


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--no-dry-run", action="store_true", default=False)
    args = parser.parse_args()

    process_file(read_csv_file())

    if args.no_dry_run:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
