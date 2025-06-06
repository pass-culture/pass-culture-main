"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/tcoudray-pass/PC-36362-duplicate-future-offer/api/src/pcapi/scripts/duplicate_reminders/main.py

"""

import argparse
import logging

from pcapi.app import app
from pcapi.core.reminders import models as reminders_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def main() -> None:
    future_offer_reminders: list[reminders_models.FutureOfferReminder] = db.session.query(
        reminders_models.FutureOfferReminder
    ).all()

    for future_offer_reminder in future_offer_reminders:
        offer_reminder = (
            db.session.query(reminders_models.OfferReminder)
            .filter_by(userId=future_offer_reminder.userId, offerId=future_offer_reminder.futureOffer.offerId)
            .one_or_none()
        )

        if not offer_reminder:
            offer_reminder = reminders_models.OfferReminder(
                userId=future_offer_reminder.userId,
                offerId=future_offer_reminder.futureOffer.offerId,
            )
            db.session.add(offer_reminder)


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
