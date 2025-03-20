"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/pcharlet/pc-32809-script-offerer-with-one-venue-is-permanent/api/src/pcapi/scripts/offerers_with_one_venue_are_permanent/main.py

"""

import argparse
import csv
import logging
import os

from flask_sqlalchemy import BaseQuery
import sqlalchemy as sqla

from pcapi.app import app
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def extract_venues_info_to_csv(query: BaseQuery) -> None:
    venues_query_for_csv = query.with_entities(
        offerers_models.Venue.id, offerers_models.VenueContact.email, offerers_models.Venue.hasOffers
    ).join(offerers_models.VenueContact, offerers_models.VenueContact.venueId == offerers_models.Venue.id)
    output_file = f"{os.environ['OUTPUT_DIRECTORY']}/export_venues_updated_to_permanent.csv"
    logger.info("Exporting data to %s", output_file)

    with open(output_file, "w", encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile, dialect=csv.excel, delimiter=";", quoting=csv.QUOTE_NONNUMERIC)
        writer.writerow(["Venue id", "Venue contact email", "Venue has offer"])
        for row in venues_query_for_csv.all():
            writer.writerow(row)


def get_venues_to_update_query() -> BaseQuery:
    venues_to_update_subquery = (
        offerers_models.Venue.query.with_entities(offerers_models.Venue.id)
        .filter(offerers_models.Venue.isPermanent.is_(False), offerers_models.Venue.isVirtual.is_(False))
        .join(offerers_models.Offerer, offerers_models.Venue.managingOffererId == offerers_models.Offerer.id)
        .group_by(offerers_models.Venue.id)
        .having(sqla.func.count(offerers_models.Offerer.managedVenues) == 1)
    )
    return offerers_models.Venue.query.filter(offerers_models.Venue.id.in_(venues_to_update_subquery))


def update_venues(query: BaseQuery) -> None:
    query.update({offerers_models.Venue.isPermanent: True}, synchronize_session=False)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    venues_query = get_venues_to_update_query()
    extract_venues_info_to_csv(venues_query)

    if args.not_dry:
        logger.info("Finished")
        update_venues(venues_query)
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
