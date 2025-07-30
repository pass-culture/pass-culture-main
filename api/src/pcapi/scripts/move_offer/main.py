import argparse
import csv
import logging
import os
import typing

from pcapi.app import app
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers import repository as offerers_repository
from pcapi.core.offers import api as offer_api
from pcapi.core.offers import models as offers_models
from pcapi.models import db
from pcapi.repository.session_management import atomic
from pcapi.repository.session_management import mark_transaction_as_invalid


logger = logging.getLogger(__name__)

OFFER_ID_HEADER = "offer_id"
ORIGIN_VENUE_ID_HEADER = "origin_venue_id"
DESTINATION_VENUE_ID_HEADER = "destination_venue_id"

app.app_context().push()


def _get_offers_rows() -> typing.Iterator[dict]:
    namespace_dir = os.path.dirname(os.path.abspath(__file__))
    with open(f"{namespace_dir}/offers.csv", "r", encoding="utf-8") as csv_file:
        csv_rows = csv.DictReader(csv_file, delimiter=",")
        yield from csv_rows


def _check_destination_venue_validity(
    origin_venue: offerers_models.Venue, destination_venue: offerers_models.Venue
) -> bool:
    venues_choices = offerers_repository.get_offerers_venues_with_pricing_point(
        origin_venue,
        include_without_pricing_points=True,
        only_similar_pricing_points=True,
        filter_same_bank_account=True,
    )
    if not venues_choices:
        logger.info(
            "No compatible venue was found for venue %d. Destination venue was %d",
            origin_venue.id,
            destination_venue.id,
        )
        return True
    if destination_venue not in venues_choices:
        logger.info("Destination venue %d is not valid for venue %d", destination_venue.id, origin_venue.id)
        return True
    return False


def _check_origin_venue_validity(offer: offers_models.Offer, origin_venue: offerers_models.Venue) -> bool:
    if offer.venue != origin_venue:
        logger.info("origin venue %d different from offer %d venue", origin_venue.id, offer.id)
        return True
    return False


def _check_venues_validity(
    offer: offers_models.Offer,
    origin_venue: offerers_models.Venue | None,
    origin_venue_id: int,
    destination_venue: offerers_models.Venue | None,
    destination_venue_id: int,
) -> bool:
    origin_venue_validity = False
    destination_venue_validity = False
    if origin_venue is None:
        logger.info("Origin venue not found. id: %d", origin_venue_id)
        return True
    else:
        origin_venue_validity = _check_origin_venue_validity(offer, origin_venue)

    if destination_venue is None:
        logger.info("Destination venue not found. id: %d", destination_venue_id)
        return True
    elif origin_venue:
        destination_venue_validity = _check_destination_venue_validity(origin_venue, destination_venue)
    return origin_venue_validity or destination_venue_validity


def _move_offer(
    offer: offers_models.Offer, origin_venue: offerers_models.Venue, destination_venue: offerers_models.Venue
) -> None:
    offer_api.move_offer(offer, destination_venue)
    logger.info(
        "Individual offer' venue has changed",
        extra={
            "origin_venue_id": origin_venue.id,
            "destination_venue_id": destination_venue.id,
            "offer_id": offer.id,
            "offers_type": "individual",
        },
        technical_message_id="offer.move",
    )


@atomic()
def _move_offers_by_ids(dry_run: bool) -> None:
    for row in _get_offers_rows():
        offer_id = int(row[OFFER_ID_HEADER])
        origin_venue_id = int(row[ORIGIN_VENUE_ID_HEADER])
        destination_venue_id = int(row[DESTINATION_VENUE_ID_HEADER])
        logger.info(
            "Starting to move offer %d from venue (origin): %d to venue (destination): %d",
            offer_id,
            origin_venue_id,
            destination_venue_id,
        )

        offer = db.session.query(offers_models.Offer).filter(offers_models.Offer.id == offer_id).one_or_none()
        if offer is None:
            logger.info("Offer not found. id: %d", offer_id)
            continue
        elif offer.isDigital is False:
            logger.info("Offer %d is not digital", offer_id)
            continue

        origin_venue = (
            db.session.query(offerers_models.Venue).filter(offerers_models.Venue.id == origin_venue_id).one_or_none()
        )
        destination_venue = (
            db.session.query(offerers_models.Venue)
            .filter(offerers_models.Venue.id == destination_venue_id)
            .one_or_none()
        )

        invalidity_reason = _check_venues_validity(
            offer, origin_venue, origin_venue_id, destination_venue, destination_venue_id
        )

        if invalidity_reason:
            continue
        else:
            with atomic():
                _move_offer(offer, origin_venue, destination_venue)

                if dry_run:
                    db.session.flush()
                    mark_transaction_as_invalid()
                else:
                    logger.info(
                        "Offer %d moved from venue %d to venue %d", offer_id, origin_venue_id, destination_venue_id
                    )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=True)
    args = parser.parse_args()

    try:
        _move_offers_by_ids(dry_run=args.dry_run)
    except:
        db.session.rollback()
        raise
    else:
        if args.dry_run:
            db.session.rollback()
            logger.info("Finished dry run, rollback")
        else:
            db.session.commit()
            logger.info("Finished")
