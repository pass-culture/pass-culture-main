"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/contact-email-none-collective-offers/api/src/pcapi/scripts/collective_contact_email/main.py

"""

import argparse
import logging

from sqlalchemy import orm as sa_orm

from pcapi.app import app
from pcapi.core.educational import models as educational_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def process_offers(
    model: type[educational_models.CollectiveOffer] | type[educational_models.CollectiveOfferTemplate],
) -> None:
    collective_offers: "sa_orm.Query[educational_models.CollectiveOffer | educational_models.CollectiveOfferTemplate]" = db.session.query(
        model
    ).filter(model.contactEmail == "")

    logger.info("Found %s collective offers with empty contactEmail", collective_offers.count())

    for collective_offer in collective_offers:
        collective_offer.contactEmail = None
        db.session.add(collective_offer)


def main() -> None:
    logger.info("Starting to process collective offers")
    process_offers(model=educational_models.CollectiveOffer)
    logger.info("Finished processing collective offers")

    logger.info("Starting to process collective offer templates")
    process_offers(model=educational_models.CollectiveOfferTemplate)
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
