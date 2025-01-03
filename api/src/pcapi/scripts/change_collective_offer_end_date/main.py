import argparse
import datetime
import logging

from pcapi.app import app
from pcapi.core.educational import models as educational_models
from pcapi.models import db


logger = logging.getLogger(__name__)

app.app_context().push()

OFFER_ID = 547856

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    offer: educational_models.CollectiveOffer = educational_models.CollectiveOffer.query.filter(
        educational_models.CollectiveOffer.id == OFFER_ID
    ).one()

    stock = offer.collectiveStock

    if stock.endDatetime.year != 2220:
        raise ValueError("End year is not as expected")

    # tomorrow at the same time as original value
    time = stock.endDatetime.time()
    stock.endDatetime = datetime.datetime.combine(datetime.date.today() + datetime.timedelta(days=1), time=time)
    logger.info("Setting endDatetime to %s", stock.endDatetime)

    if args.not_dry:
        logger.info("Finished correcting end date")
        db.session.commit()
    else:
        logger.info("Finished dry run for correcting end date, rollback")
        db.session.rollback()
