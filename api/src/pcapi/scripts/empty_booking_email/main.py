import argparse
import logging

from sqlalchemy.orm import joinedload

from pcapi.app import app
from pcapi.core.offerers import models as offerer_models
from pcapi.core.offers import models as offer_models
from pcapi.models import db


logger = logging.getLogger(__name__)

app.app_context().push()

OFFER_ID = 2801

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    offer: offer_models.Offer = (
        offer_models.Offer.query.filter(offer_models.Offer.id == OFFER_ID)
        .options(joinedload(offer_models.Offer.venue))
        .one()
    )

    offerer_id = offer.venue.managingOffererId

    invalid_offers = (
        offer_models.Offer.query.join(offer_models.Offer.venue)
        .filter(offer_models.Offer.bookingEmail == " ", offerer_models.Venue.managingOffererId == offerer_id)
        .all()
    )
    logger.info("Found %s offers with invalid bookingEmail for offerer with id %s", len(invalid_offers), offerer_id)

    for invalid_offer in invalid_offers:
        if invalid_offer.bookingEmail != " ":
            raise ValueError()

        invalid_offer.bookingEmail = None

    db.session.flush()

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
