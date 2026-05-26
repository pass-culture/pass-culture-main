"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=pc-41991-move-offers \
  -f NAMESPACE=move_offers \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging
from functools import partial

import sqlalchemy.orm as sa_orm

from pcapi.core import search
from pcapi.core.bookings import models as bookings_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers.api import get_or_create_offer_location
from pcapi.core.offers import models as offers_models
from pcapi.core.offers.api import get_or_create_label
from pcapi.core.search import IndexationReason
from pcapi.models import db
from pcapi.utils.transaction_manager import on_commit


logger = logging.getLogger(__name__)


def main(source_venue_id: int, destination_venue_id: int, destination_offerer_id: int, offer_ids: list[int]) -> None:
    destination_venue = (
        db.session.query(offerers_models.Venue)
        .filter(
            offerers_models.Venue.id == destination_venue_id,
            offerers_models.Venue.managingOffererId == destination_offerer_id,
        )
        .options(sa_orm.joinedload(offerers_models.Venue.venueProviders))
        .one()
    )
    destination_provider_ids = [venue_provider.providerId for venue_provider in destination_venue.venueProviders]

    offers = (
        db.session.query(offers_models.Offer)
        .filter(offers_models.Offer.venueId == source_venue_id, offers_models.Offer.id.in_(offer_ids))
        .options(
            sa_orm.joinedload(offers_models.Offer.priceCategories).joinedload(
                offers_models.PriceCategory.priceCategoryLabel
            ),
            sa_orm.joinedload(offers_models.Offer.offererAddress),
        )
        .all()
    )
    logger.info("%d offers found", len(offers))
    assert len(offers) == len(offer_ids)

    for offer in offers:
        logging.info("Move offer %d to venue %d", offer.id, destination_venue_id)
        if offer.lastProviderId:
            assert offer.lastProviderId in destination_provider_ids
        offer.venueId = destination_venue_id
        if offer.offererAddress:
            offer.offererAddress = get_or_create_offer_location(
                offerer_id=destination_offerer_id,
                address_id=offer.offererAddress.addressId,
                venue_id=destination_venue_id,
                label=offer.offererAddress.label,
            )
        for price_category in offer.priceCategories:
            price_category.priceCategoryLabel = get_or_create_label(price_category.label, destination_venue)
            db.session.add(price_category)
        db.session.add(offer)
        on_commit(partial(search.async_index_offer_ids, [offer.id], reason=IndexationReason.OFFER_UPDATE))
        db.session.flush()

    bookings = (
        db.session.query(bookings_models.Booking)
        .join(bookings_models.Booking.stock)
        .filter(
            bookings_models.Booking.venueId == source_venue_id,
            offers_models.Stock.offerId.in_(offer_ids),
        )
        .all()
    )
    logger.info("%d bookings found", len(bookings))

    for booking in bookings:
        logging.info("Move booking %s to venue %d", booking.token, destination_venue_id)
        assert booking.status not in (
            bookings_models.BookingStatus.USED,
            bookings_models.BookingStatus.PENDING_REIMBURSEMENT,
            bookings_models.BookingStatus.REIMBURSED,
        )
        booking.venueId = destination_venue_id
        db.session.add(booking)
        db.session.flush()


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--old-venue-id", type=int, required=True)
    parser.add_argument("--new-venue-id", type=int, required=True)
    parser.add_argument("--new-offerer-id", type=int, required=True)
    parser.add_argument("--offer-ids", nargs="+", type=int, required=True)
    args = parser.parse_args()

    main(args.old_venue_id, args.new_venue_id, args.new_offerer_id, args.offer_ids)

    if args.apply:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
