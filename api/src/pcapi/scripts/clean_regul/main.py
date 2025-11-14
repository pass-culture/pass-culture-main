"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=pcharlet/pc-38676-save-forgotten-collective-objects-during-regul \
  -f NAMESPACE=clean_regul \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import csv
import logging
import os
import typing

from pcapi.app import app
from pcapi.core.educational import models as educational_models
from pcapi.core.educational.api import offer as educational_api
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)

SOFT_DELETED_VENUE_ID_HEADER = "soft_deleted_venue_ids"
DESTINATION_VENUE_HEADER = "destination_venue_ids"


def _read_csv_file(filename: str) -> typing.Iterator[dict[str, str]]:
    namespace_dir = os.path.dirname(os.path.abspath(__file__))
    with open(f"{namespace_dir}/{filename}.csv", "r", encoding="utf-8") as csv_file:
        csv_rows = csv.DictReader(csv_file, delimiter=",")
        yield from csv_rows


def _move_collective_offers(origin_venue: offerers_models.Venue, destination_venue: offerers_models.Venue) -> None:
    collective_offer_ids = []
    collective_offer_list = list(origin_venue.collectiveOffers)
    for collective_offer in collective_offer_list:
        educational_api.move_collective_offer_for_regularization(collective_offer, destination_venue)
        collective_offer_ids.append(collective_offer.id)
    logger.info(
        "Collective offers' venue has changed",
        extra={
            "origin_venue_id": origin_venue.id,
            "destination_venue_id": destination_venue.id,
            "collective_offer_ids": collective_offer_ids,
            "offers_type": "collective",
        },
        technical_message_id="collective_offer.move",
    )


def _move_collective_bookings(origin_venue: offerers_models.Venue, destination_venue: offerers_models.Venue) -> None:
    collective_booking_count = (
        db.session.query(educational_models.CollectiveBooking)
        .filter(educational_models.CollectiveBooking.venueId == origin_venue.id)
        .update({"venueId": destination_venue.id}, synchronize_session=False)
    )
    logger.info(
        "Update %d collective booking(s), from venue %d to venue %d",
        collective_booking_count,
        origin_venue.id,
        destination_venue.id,
    )


def _move_collective_offer_template(
    origin_venue: offerers_models.Venue, destination_venue: offerers_models.Venue
) -> None:
    collective_offer_templates = db.session.query(educational_models.CollectiveOfferTemplate).filter(
        educational_models.CollectiveOfferTemplate.venueId == origin_venue.id
    )
    collective_offer_templates.update({"venueId": destination_venue.id}, synchronize_session=False)
    collective_offer_template_ids = [
        collective_offer_template.id for collective_offer_template in collective_offer_templates.all()
    ]
    logger.info(
        "Collective offer templates' venue has changed",
        extra={
            "origin_venue_id": origin_venue.id,
            "destination_venue_id": destination_venue.id,
            "collective_offer_template_ids": collective_offer_template_ids,
            "offers_type": "collective",
        },
        technical_message_id="collective_offer_template.move",
    )


@atomic()
def main(not_dry: bool) -> None:
    if not not_dry:
        logger.info("Dry run mode enabled, no changes will be made to the database")
        mark_transaction_as_invalid()
    rows = list(_read_csv_file("venues_with_forgotten_objects"))
    for row in rows:
        origin_venue = (
            db.session.query(offerers_models.Venue)
            .execution_options(include_deleted=True)
            .filter(offerers_models.Venue.id == row[SOFT_DELETED_VENUE_ID_HEADER])
            .one()
        )
        destination_venue = (
            db.session.query(offerers_models.Venue)
            .filter(offerers_models.Venue.id == row[DESTINATION_VENUE_HEADER])
            .one()
        )
        with atomic():
            _move_collective_offers(origin_venue, destination_venue)
            _move_collective_bookings(origin_venue, destination_venue)
            _move_collective_offer_template(origin_venue, destination_venue)


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
