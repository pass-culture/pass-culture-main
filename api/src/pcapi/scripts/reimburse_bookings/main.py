"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/PC-37387-reimburse-some-bookings/api/src/pcapi/scripts/reimburse_bookings/main.py

"""

import argparse
import logging

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from pcapi.app import app
from pcapi.core.bookings.models import Booking
from pcapi.core.finance.models import Recredit
from pcapi.core.finance.models import RecreditType
from pcapi.core.users.models import User
from pcapi.models import db


logger = logging.getLogger(__name__)

BOOKING_TO_REIMBURSE_TOKENS = [
    "GWUDA7",
    "7LKFET",
    "AQNVUF",
    "TQBV5L",
    "GFYS52",
    "VLVDYG",
]


def reimburse_bookings(not_dry: bool, tokens: list[str] | None = None) -> None:
    if tokens is None:
        tokens = BOOKING_TO_REIMBURSE_TOKENS

    bookings = _get_bookings(tokens)
    for booking in bookings:
        _reimburse_booking(booking)


def _get_bookings(tokens: list[str]) -> list[Booking]:
    bookings_query = (
        select(Booking).where(Booking.token.in_(tokens)).options(joinedload(Booking.user).selectinload(User.deposits))
    )
    return db.session.scalars(bookings_query).all()


def _reimburse_booking(booking: Booking) -> None:
    deposit = booking.user.deposit
    if not deposit:
        logger.warning("no deposit found for user %s", booking.user.id)
        return

    recredit = Recredit(
        deposit=deposit,
        amount=booking.quantity * booking.stock.price,
        recreditType=RecreditType.MANUAL_MODIFICATION,
        comment=f"(PC-37387) Remboursement de la contremarque {booking.token}",
    )
    deposit.amount += recredit.amount

    logger.info(f"recredited {recredit.amount} euros to {booking.user = } and {deposit = }")

    db.session.add(recredit)
    db.session.flush()


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    reimburse_bookings(not_dry=args.not_dry)

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
