import argparse
import logging

import sqlalchemy as sa

from pcapi.app import app
from pcapi.core.educational import models as educational_models
from pcapi.core.offerers import models as offerer_models
from pcapi.models import db


logger = logging.getLogger(__name__)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    collective_offers: list[educational_models.CollectiveOffer] = (
        db.session.query(educational_models.CollectiveOffer)
        .outerjoin(
            offerer_models.Venue,
            offerer_models.Venue.id
            == sa.cast(educational_models.CollectiveOffer.offerVenue.op("->>")("venueId"), sa.Integer),
        )
        .filter(
            educational_models.CollectiveOffer.offerVenue.op("->>")("addressType")
            == educational_models.OfferAddressType.OFFERER_VENUE.value,
            offerer_models.Venue.id.is_(None),
        )
        .all()
    )

    logger.info(
        "Found %s collective offers with invalid offerVenue.venueId, ids -> %s",
        len(collective_offers),
        [o.id for o in collective_offers],
    )

    collective_offer_templates: list[educational_models.CollectiveOfferTemplate] = (
        db.session.query(educational_models.CollectiveOfferTemplate)
        .outerjoin(
            offerer_models.Venue,
            offerer_models.Venue.id
            == sa.cast(educational_models.CollectiveOfferTemplate.offerVenue.op("->>")("venueId"), sa.Integer),
        )
        .filter(
            educational_models.CollectiveOfferTemplate.offerVenue.op("->>")("addressType")
            == educational_models.OfferAddressType.OFFERER_VENUE.value,
            offerer_models.Venue.id.is_(None),
        )
        .all()
    )

    logger.info(
        "Found %s collective offer templates with invalid offerVenue.venueId, ids -> %s",
        len(collective_offer_templates),
        [ot.id for ot in collective_offer_templates],
    )

    offers: list[educational_models.CollectiveOffer | educational_models.CollectiveOfferTemplate] = [
        *collective_offers,
        *collective_offer_templates,
    ]
    for offer in offers:
        offer.offerVenue["venueId"] = offer.venueId
        db.session.add(offer)

    db.session.flush()

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
