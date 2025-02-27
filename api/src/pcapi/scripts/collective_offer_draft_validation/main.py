import argparse
import logging

import sqlalchemy as sa
from sqlalchemy import orm as sa_orm

from pcapi.app import app
from pcapi.core.educational import models as educational_models
from pcapi.models import db
from pcapi.models import offer_mixin


logger = logging.getLogger(__name__)

if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    collective_offers: "sa_orm.Query[educational_models.CollectiveOffer]" = db.session.query(
        educational_models.CollectiveOffer
    ).filter(
        educational_models.CollectiveOffer.validation == offer_mixin.OfferValidationStatus.DRAFT,
        sa.or_(
            educational_models.CollectiveOffer.lastValidationDate.is_not(None),
            educational_models.CollectiveOffer.lastValidationType.is_not(None),
            educational_models.CollectiveOffer.lastValidationAuthorUserId.is_not(None),
        ),
    )

    logger.info("Found %s collective offers to fix", collective_offers.count())

    for collective_offer in collective_offers.yield_per(1_000):
        collective_offer.lastValidationDate = None
        collective_offer.lastValidationType = None
        collective_offer.lastValidationAuthorUserId = None

    db.session.flush()

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
