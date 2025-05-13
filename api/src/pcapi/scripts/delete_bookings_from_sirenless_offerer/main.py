"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/master/api/src/pcapi/scripts/delete_bookings_from_sirenless_offerer/main.py

"""

import argparse
import logging

import sqlalchemy as sa

from pcapi.app import app
from pcapi.core.achievements import models as achievements_models
from pcapi.core.bookings import models as bookings_models
from pcapi.core.finance import models as finance_models
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def main(not_dry: bool) -> None:
    bookings_to_delete_query = (
        db.session.query(bookings_models.Booking)
        .join(offerers_models.Offerer, offerers_models.Offerer.id == bookings_models.Booking.offererId)
        .filter(offerers_models.Offerer.siren.is_(None))
    )
    logger.info(f"{bookings_to_delete_query.count()} bookings to delete")
    booking_ids = {booking.id for booking in bookings_to_delete_query}

    achievements_to_delete_query = db.session.query(achievements_models.Achievement).filter(
        achievements_models.Achievement.bookingId.in_(booking_ids)
    )

    finance_events_to_delete_query = db.session.query(finance_models.FinanceEvent).filter(
        finance_models.FinanceEvent.bookingId.in_(booking_ids)
    )
    pricings_to_delete_query = db.session.query(finance_models.Pricing).filter(
        finance_models.Pricing.bookingId.in_(booking_ids)
    )
    pricing_ids = {pricing.id for pricing in pricings_to_delete_query}
    pricing_lines_to_delete_query = db.session.query(finance_models.PricingLine).filter(
        finance_models.PricingLine.pricingId.in_(pricing_ids)
    )

    payment_count = (
        db.session.query(finance_models.Payment).filter(finance_models.Payment.bookingId.in_(booking_ids)).count()
    )
    cashflow_count = (
        db.session.query(finance_models.CashflowPricing)
        .filter(finance_models.CashflowPricing.pricingId.in_(pricing_ids))
        .count()
    )
    if payment_count > 0 or cashflow_count > 0:
        logger.error("We can't delete invoiced data")
        return

    achievements_to_delete_query.delete()
    if args.not_dry:
        db.session.commit()
    pricing_lines_to_delete_query.delete()
    if args.not_dry:
        db.session.commit()
    pricings_to_delete_query.delete()
    if args.not_dry:
        db.session.commit()
    finance_events_to_delete_query.delete()
    if args.not_dry:
        db.session.commit()
    db.session.query(bookings_models.Booking).filter(bookings_models.Booking.id.in_(booking_ids)).delete()
    if args.not_dry:
        db.session.commit()


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()
    db.session.execute(sa.text("set session statement_timeout = '500s'"))

    main(args.not_dry)

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
