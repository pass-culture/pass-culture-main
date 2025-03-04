import argparse
import logging

from sqlalchemy import orm as sa_orm

from pcapi.app import app
from pcapi.core.educational import models as educational_models
from pcapi.models import db


logger = logging.getLogger(__name__)

OFFER_IDS = [
    338296,
    338478,
    338513,
    338536,
    338551,
    607519,
    631029,
    631078,
    631126,
    631153,
]

if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    collective_offers: "sa_orm.Query[educational_models.CollectiveOffer]" = db.session.query(
        educational_models.CollectiveOffer
    ).filter(educational_models.CollectiveOffer.id.in_(OFFER_IDS))

    for collective_offer in collective_offers:
        emails = collective_offer.bookingEmails

        if not (len(emails) == 1 and emails[0].endswith("@yahoo.f")):
            raise ValueError(f"Offer with id {collective_offer.id} does not have expected value")

        collective_offer.bookingEmails = [emails[0].replace("yahoo.f", "yahoo.fr")]

    db.session.flush()

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
