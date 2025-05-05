"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/fix-collective-offer-venue/api/src/pcapi/scripts/offer_venue_empty_venue_id/main.py

"""

import argparse
import logging

from sqlalchemy import orm as sa_orm

from pcapi.app import app
from pcapi.core.educational import models as educational_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def process_offers(
    offer_model: type[educational_models.CollectiveOffer] | type[educational_models.CollectiveOfferTemplate],
) -> None:
    query: "sa_orm.Query[educational_models.CollectiveOffer | educational_models.CollectiveOfferTemplate]" = (
        db.session.query(offer_model).filter(offer_model.offerVenue.op("->>")("venueId") == "")
    )

    logger.info("Found %s collective offers with offerVenue.venueId = ''", query.count())

    for collective_offer in query:
        collective_offer.offerVenue["venueId"] = None
        db.session.add(collective_offer)

    db.session.flush()


def main() -> None:
    logger.info("Starting to process collective offers")
    process_offers(offer_model=educational_models.CollectiveOffer)
    logger.info("Finished processing collective offers")

    logger.info("Starting to process collective offer templates")
    process_offers(offer_model=educational_models.CollectiveOfferTemplate)
    logger.info("Finished processing collective offer templates")


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
