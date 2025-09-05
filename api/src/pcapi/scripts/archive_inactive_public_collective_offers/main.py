"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/PC-34378-is-active-false-public-api-archive/api/src/pcapi/scripts/archive_inactive_public_collective_offers/main.py

"""

import argparse
import logging
import os

from sqlalchemy import orm as sa_orm

from pcapi.app import app
from pcapi.core.educational import models
from pcapi.models import db
from pcapi.models import offer_mixin
from pcapi.utils.date import get_naive_utc_now


logger = logging.getLogger(__name__)


def main() -> None:
    # we archive collective offers that are
    # - approved (validation=APPROVED) (other states are DRAFT, PENDING, REJECTED -> the offer is always inactive in these cases)
    # - inactive (isActive = False)
    # - not already archived (isArchived = False)
    # - with a provider (providerId is not None)
    # - with no booking (lastBooking is None)

    inactive_offers: list[models.CollectiveOffer] = (
        db.session.query(models.CollectiveOffer)
        .filter(
            models.CollectiveOffer.validation == offer_mixin.OfferValidationStatus.APPROVED,
            models.CollectiveOffer.isActive.is_(False),
            models.CollectiveOffer.isArchived == False,
            models.CollectiveOffer.providerId.is_not(None),
        )
        .order_by(models.CollectiveOffer.id)
        .options(
            sa_orm.selectinload(models.CollectiveOffer.collectiveStock).selectinload(
                models.CollectiveStock.collectiveBookings
            )
        )
        .all()
    )

    count = 0
    now = get_naive_utc_now()
    archived_offer_ids = []
    for offer in inactive_offers:
        if offer.lastBooking is None:
            count += 1
            offer.dateArchived = now
            archived_offer_ids.append(f"{str(offer.id)}\n")

    logger.info("Found %s offers to archive", count)

    with open(f"{os.environ.get('OUTPUT_DIRECTORY')}/archived_offer_ids.txt", "w", encoding="utf8") as f:
        f.writelines(archived_offer_ids)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    main()

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
