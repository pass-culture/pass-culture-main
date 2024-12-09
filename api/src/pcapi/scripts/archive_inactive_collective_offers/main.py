import argparse
import datetime
import logging
import os
import typing

import sqlalchemy as sa

from pcapi.app import app
from pcapi.core.educational import models as educational_models
from pcapi.models import db
from pcapi.models import offer_mixin


logger = logging.getLogger(__name__)

app.app_context().push()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    inactive_offers: typing.Iterable[educational_models.CollectiveOffer] = (
        educational_models.CollectiveOffer.query.filter(
            educational_models.CollectiveOffer.validation == offer_mixin.OfferValidationStatus.APPROVED,
            educational_models.CollectiveOffer.isActive.is_(False),
            educational_models.CollectiveOffer.isArchived == False,
            educational_models.CollectiveOffer.providerId.is_(None),
        )
        .order_by(educational_models.CollectiveOffer.id)
        .options(
            sa.orm.selectinload(educational_models.CollectiveOffer.collectiveStock).selectinload(
                educational_models.CollectiveStock.collectiveBookings
            )
        )
        .yield_per(1000)
    )

    now = datetime.datetime.utcnow()
    archived_offer_ids = []
    for offer in inactive_offers:
        if offer.lastBooking is None:
            offer.dateArchived = now
            archived_offer_ids.append(f"{str(offer.id)}\n")

    with open(f"{os.environ.get('OUTPUT_DIRECTORY')}/archived_offer_ids.txt", "w", encoding="utf8") as f:
        f.writelines(archived_offer_ids)

    if args.not_dry:
        logger.info("Finished archiving offers")
        db.session.commit()
    else:
        logger.info("Finished dry run for archiving offers, rollback")
        db.session.rollback()
