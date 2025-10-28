"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml   -f ENVIRONMENT=testing   -f BRANCH_NAME=pcharlet/pc-38539-script-regul-clean   -f NAMESPACE=clean_regul   -f SCRIPT_ARGUMENTS="";

"""

import argparse
import csv
import logging
import os
import typing

from pcapi.app import app
from pcapi.core.bookings import models as bookings_models
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import api as offer_api
from pcapi.core.offers import models as offer_models
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)

SOFT_DELETED_VENUE_ID_HEADER = "soft_deleted_venue_ids"
DESTINATION_VENUE = "destination_venue_ids"


def _read_csv_file(filename: str) -> typing.Iterator[dict[str, str]]:
    namespace_dir = os.path.dirname(os.path.abspath(__file__))
    with open(f"{namespace_dir}/{filename}.csv", "r", encoding="utf-8") as csv_file:
        csv_rows = csv.DictReader(csv_file, delimiter=",")
        yield from csv_rows


def _move_individual_offers(origin_venue: offerers_models.Venue, destination_venue: offerers_models.Venue) -> None:
    offer_ids = []
    offer_list = list(origin_venue.offers)
    for offer in offer_list:
        offer_api.move_offer(offer, destination_venue)
        offer_ids.append(offer.id)
        db.session.flush()
    logger.info(
        "Individual offers' venue has changed",
        extra={
            "origin_venue_id": origin_venue.id,
            "destination_venue_id": destination_venue.id,
            "offer_ids": offer_ids,
            "offers_type": "individual",
        },
        technical_message_id="offer.move",
    )


def _move_bookings(origin_venue: offerers_models.Venue, destination_venue: offerers_models.Venue) -> None:
    booking_count = (
        db.session.query(bookings_models.Booking)
        .filter(bookings_models.Booking.venueId == origin_venue.id)
        .update({"venueId": destination_venue.id}, synchronize_session=False)
    )
    logger.info("Update %d booking(s), from venue %d to venue %d", booking_count, origin_venue.id, destination_venue.id)


def _move_price_category_label(origin_venue: offerers_models.Venue, destination_venue: offerers_models.Venue) -> None:
    origin_price_category_labels = (
        db.session.query(offer_models.PriceCategoryLabel)
        .filter(offer_models.PriceCategoryLabel.venueId == origin_venue.id)
        .all()
    )
    for origin_price_category_label in origin_price_category_labels:
        existing_price_category_label = (
            db.session.query(offer_models.PriceCategoryLabel)
            .filter(
                offer_models.PriceCategoryLabel.venueId == destination_venue.id,
                offer_models.PriceCategoryLabel.label == origin_price_category_label.label,
            )
            .one_or_none()
        )
        if existing_price_category_label:
            db.session.query(offer_models.PriceCategory).filter(
                offer_models.PriceCategory.priceCategoryLabelId == origin_price_category_label.id
            ).update(
                {"priceCategoryLabelId": existing_price_category_label.id},
                synchronize_session=False,
            )
            logger.info(
                "Update PriceCategory from label %d (venue %d) to label %d (venue %d)",
                origin_price_category_label.id,
                origin_venue.id,
                existing_price_category_label.id,
                destination_venue.id,
            )
        else:
            origin_price_category_label.venueId = destination_venue.id
            db.session.add(origin_price_category_label)
            logger.info(
                "Update PriceCategoryLabel %d from venue %d to venue %d",
                origin_price_category_label.id,
                origin_venue.id,
                destination_venue.id,
            )


def _move_finance_incident(origin_venue: offerers_models.Venue, destination_venue: offerers_models.Venue) -> None:
    finance_incident_count = (
        db.session.query(finance_models.FinanceIncident)
        .filter(finance_models.FinanceIncident.venueId == origin_venue.id)
        .update({"venueId": destination_venue.id}, synchronize_session=False)
    )
    logger.info(
        "Update %d finance incident(s), from venue %d to venue %d",
        finance_incident_count,
        origin_venue.id,
        destination_venue.id,
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
            db.session.query(offerers_models.Venue).filter(offerers_models.Venue.id == row[DESTINATION_VENUE]).one()
        )
        with atomic():
            _move_individual_offers(origin_venue, destination_venue)
            _move_bookings(origin_venue, destination_venue)
            _move_price_category_label(origin_venue, destination_venue)
            _move_finance_incident(origin_venue, destination_venue)


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
