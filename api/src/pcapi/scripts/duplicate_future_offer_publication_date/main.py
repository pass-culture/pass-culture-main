"""
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/tcoudray-pass/PC-36178-script-to-duplicate-future_offers-in-publication-date/api/src/pcapi/scripts/duplicate_future_offer_publicationDate/main.py
"""

import argparse
import logging

from pcapi.app import app
from pcapi.core.offers import models as offers_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def main() -> None:
    future_offers_query: list[offers_models.FutureOffer] = db.session.query(offers_models.FutureOffer).all()

    for future_offer in future_offers_query:
        offer: offers_models.Offer = db.session.query(offers_models.Offer).filter_by(id=future_offer.offerId).one()

        should_duplicate_future_offer_publicationDate = (
            not offer.publicationDatetime  # offer does not already have a publicationDatetime
            and (
                (offer.isActive and future_offer.isSoftDeleted)  # i.e. has been published by the CRON job
                or (not offer.isActive and future_offer.isWaitingForPublication)  # i.e. is waiting to be published
            )
        )

        if should_duplicate_future_offer_publicationDate:
            offer.publicationDatetime = future_offer.publicationDate
            offer.bookingAllowedDatetime = future_offer.publicationDate
            db.session.flush()
            logger.info(
                "publicationDate was duplicated",
                extra={
                    "future_offer": {
                        "id": future_offer.id,
                        "publicationDate": future_offer.publicationDate,
                        "isSoftDeleted": future_offer.isSoftDeleted,
                    },
                    "offer": {"id": offer.id},
                },
            )
        else:
            logger.warning(
                "publicationDate was not duplicated",
                extra={
                    "future_offer": {
                        "id": future_offer.id,
                        "publicationDate": future_offer.publicationDate,
                        "isSoftDeleted": future_offer.isSoftDeleted,
                    },
                    "offer": {"id": offer.id},
                },
            )


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
