import argparse
import logging

import sqlalchemy as sa

from pcapi.core.educational import models as educational_models
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import exceptions as offerers_exceptions
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.flask_app import app
from pcapi.models import db


logger = logging.getLogger(__name__)


def _venue_has_individual_offers(venueId: int) -> bool:
    return db.session.query(offers_models.Offer.query.filter(offers_models.Offer.venueId == venueId).exists()).scalar()


def _venue_has_collective_offers(venueId: int) -> bool:
    return (
        db.session.query(
            educational_models.CollectiveOffer.query.filter(
                educational_models.CollectiveOffer.venueId == venueId
            ).exists()
        ).scalar()
        or db.session.query(
            educational_models.CollectiveOfferTemplate.query.filter(
                educational_models.CollectiveOfferTemplate.venueId == venueId
            ).exists()
        ).scalar()
    )


def delete_venues_without_offers(dry_run: bool) -> None:
    query = db.session.execute(
        sa.select(offerers_models.Venue.id)
        .select_from(offerers_models.Venue)
        .filter(offerers_models.Venue.isVirtual == True)
    ).yield_per(100)

    deleted_venues_count = 0

    for (venueId,) in query:
        if not (_venue_has_individual_offers(venueId) or _venue_has_collective_offers(venueId)):
            try:
                offerers_api.delete_venue(venueId)
                deleted_venues_count += 1
                logger.info("Delete Virtual Venue #%s", str(venueId))
            except offerers_exceptions.CannotDeleteVenueWithBookingsException:
                # theoretically should not happen
                logger.info("Virtual Venue #%s could not be deleted because it has bookings", str(venueId))

        # commit every 100 deleted venues
        if deleted_venues_count % 100 == 0:
            if not dry_run:
                db.session.commit()
            else:
                db.session.rollback()

    # commit remaining deletions
    if not dry_run:
        db.session.commit()
    else:
        db.session.rollback()


if __name__ == "__main__":
    app.app_context().push()
    parser = argparse.ArgumentParser(description="Delete virtual venues with no offer")
    parser.add_argument("--dry-run", action=argparse.BooleanOptionalAction)
    args = parser.parse_args()

    delete_venues_without_offers(args.dry_run)
