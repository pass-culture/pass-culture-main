import argparse
import logging

from pcapi.app import app
from pcapi.core.educational import models as educational_models
from pcapi.models import db


logger = logging.getLogger(__name__)

app.app_context().push()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    invalid_offers = educational_models.CollectiveOffer.query.filter(
        educational_models.CollectiveOffer.offerVenue.op("->>")("otherAddress").is_(None)
    ).all()

    logger.info("Found %s offers with invalid offerVenue", len(invalid_offers))
    try:
        for offer in invalid_offers:
            logger.info("Collective offer with id %s is invalid, fixing", offer.id)

            if offer.offerVenue["otherAddress"] is not None:
                raise ValueError(f"Offer with id {offer.id} does not have otherAddress set to None")

            offer.offerVenue["otherAddress"] = ""
    except:
        db.session.rollback()
        raise

    if args.not_dry:
        logger.info("Committing fixed offerVenue fields")
        db.session.commit()
    else:
        logger.info("Finished dry run for fixing offerVenue field, rollbacking")
        db.session.rollback()
