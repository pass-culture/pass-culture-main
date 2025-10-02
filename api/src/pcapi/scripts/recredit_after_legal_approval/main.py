"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/pc-38223-recredit/api/src/pcapi/scripts/recredit_after_legal_approval/main.py

Recrédit exceptionnel validé par le service juridique suite à contestation.
Les références ne sont pas publiques et seront passées en paramètres.
"""

import argparse
import logging

from pcapi.app import app
from pcapi.core.bookings import models as bookings_models
from pcapi.core.finance import models as finance_models
from pcapi.core.users import api as users_api
from pcapi.models import db


logger = logging.getLogger(__name__)


def main(dry_run: bool, user_id: int, booking_token: str) -> None:
    booking = (
        db.session.query(bookings_models.Booking)
        .filter(
            bookings_models.Booking.userId == user_id,
            bookings_models.Booking.token == booking_token,
            bookings_models.Booking.status == bookings_models.BookingStatus.REIMBURSED,
        )
        .one()
    )

    deposit = booking.deposit
    assert deposit  # helps mypy

    previous_remaining_credit = users_api.get_domains_credit(booking.user).all.remaining  # type: ignore[union-attr]

    db.session.add(
        finance_models.Recredit(
            deposit=deposit,
            amount=booking.amount,
            recreditType=finance_models.RecreditType.MANUAL_MODIFICATION,
            comment=f"PC-38223 - Recrédit exceptionnel validé par le service juridique suite à une contestation sur la réservation {booking_token}",
        )
    )
    deposit.amount += booking.amount
    db.session.add(deposit)
    db.session.flush()

    new_remaining_credit = users_api.get_domains_credit(booking.user).all.remaining  # type: ignore[union-attr]

    logger.info(
        "Exceptional recredit. Remaining: %s € -> %s €",
        previous_remaining_credit,
        new_remaining_credit,
        extra={"user_id": user_id, "token": booking_token, "amount": booking.amount, "dry_run": dry_run},
    )


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    parser.add_argument("--user-id", type=int, required=True)
    parser.add_argument("--token", type=str, required=True)
    args = parser.parse_args()

    main(dry_run=not args.not_dry, user_id=args.user_id, booking_token=args.token)

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
