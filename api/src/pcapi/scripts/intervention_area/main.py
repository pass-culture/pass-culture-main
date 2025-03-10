import argparse
import logging

from sqlalchemy import orm as sa_orm

from pcapi.app import app
from pcapi.core.educational import models as educational_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def update_offer(offer: educational_models.CollectiveOffer | educational_models.CollectiveOfferTemplate) -> bool:
    address_type = offer.offerVenue["addressType"]

    if address_type == educational_models.OfferAddressType.OFFERER_VENUE.value and len(offer.interventionArea) > 0:
        offer.interventionArea = []
        return True

    return False


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    collective_offers: "sa_orm.Query[educational_models.CollectiveOffer]" = db.session.query(
        educational_models.CollectiveOffer
    )

    collective_offer_templates: "sa_orm.Query[educational_models.CollectiveOfferTemplate]" = db.session.query(
        educational_models.CollectiveOfferTemplate
    )

    fix_count = 0
    for collective_offer in collective_offers.yield_per(1000):
        offer_was_updated = update_offer(collective_offer)
        if offer_was_updated:
            fix_count += 1

    logger.info("Fixed %s collective offers with invalid interventionArea", fix_count)

    fix_template_count = 0
    for collective_offer_template in collective_offer_templates.yield_per(1000):
        offer_was_updated = update_offer(collective_offer_template)
        if offer_was_updated:
            fix_template_count += 1

    logger.info("Fixed %s collective offer templates with invalid interventionArea", fix_template_count)

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
