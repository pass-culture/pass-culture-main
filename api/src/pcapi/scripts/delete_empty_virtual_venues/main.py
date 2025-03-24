import logging

import sqlalchemy as sa

from pcapi.app import app
from pcapi.core.educational import models as educational_models
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import exceptions as offerers_exceptions
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offers import models as offers_models
from pcapi.models import db
from pcapi.repository import transaction


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


def delete_venues_without_offers() -> None:
    query = db.session.execute(
        sa.select(offerers_models.Venue.id)
        .select_from(offerers_models.Venue)
        .filter(offerers_models.Venue.isVirtual == True)
    ).yield_per(100)

    for (venueId,) in query:
        if not (_venue_has_individual_offers(venueId) or _venue_has_collective_offers(venueId)):
            try:
                with transaction():
                    offerers_api.delete_venue(venueId)

                logger.info("Delete Virtual Venue", extra={"venueId": venueId})
            except offerers_exceptions.CannotDeleteVenueWithBookingsException:
                # theoretically should not happen
                logger.warning("Virtual Venue could not be deleted because it has bookings", extra={"venueId": venueId})
            except Exception as err:  # pylint: disable=broad-exception-caught
                logger.warning(
                    "Unexpected error",
                    extra={"venueId": venueId, "exception": {"message": str(err), "name": err.__class__.__name__}},
                )


if __name__ == "__main__":
    app.app_context().push()
    delete_venues_without_offers()
