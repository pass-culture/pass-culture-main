"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/pc-35266-transfer-cancellable-bookings-to-new-deposit-script/api/src/pcapi/scripts/transfer_bookings_to_new_deposits/main.py

"""

import argparse
import logging
import math
from decimal import Decimal

from sqlalchemy.orm import selectinload

from pcapi.app import app
from pcapi.core.bookings.models import Booking
from pcapi.core.bookings.models import BookingStatus
from pcapi.core.categories.models import ReimbursementRuleChoices
from pcapi.core.external.attributes.api import update_external_user
from pcapi.core.finance.models import Deposit
from pcapi.core.finance.models import DepositType
from pcapi.core.finance.models import Recredit
from pcapi.core.finance.models import RecreditType
from pcapi.core.users.models import User
from pcapi.models import db


logger = logging.getLogger(__name__)


def main(not_dry: bool, from_id: int, batch_size: int) -> None:
    users_query = User.query.filter(
        User.deposits.any(Deposit.type == DepositType.GRANT_17_18),
        User.deposits.any(Deposit.type == DepositType.GRANT_15_17),
    ).options(selectinload(User.deposits).selectinload(Deposit.bookings))

    last_user = users_query.order_by(User.id.desc()).first()
    max_id = last_user.id
    estimated_page_number = math.ceil((max_id - from_id) / batch_size)
    current_page = 1
    logger.info("Max id = %s", max_id)

    while from_id <= max_id:
        logger.info("Processing users from id %s to %s", from_id, from_id + batch_size)
        for user in users_query.filter(User.id >= from_id, User.id < from_id + batch_size).order_by(User.id):
            underage_deposit = next(deposit for deposit in user.deposits if deposit.type == DepositType.GRANT_15_17)

            if not underage_deposit:
                logger.info("User %s has no underage deposit", user.id, extra={"user_id": user.id})  # should not happen
                continue

            if user.deposit.id == underage_deposit.id:  # should not happen because a GRANT_17_18 deposit exists
                logger.info("User %s has an underage deposit as its active one. Skipping.", user.id)
                continue

            if user.deposit.amount >= Decimal("300"):
                logger.info(
                    "User %s has a 17-18 deposit that should have been an grant 18 deposit",
                    user.id,
                    extra={"user_id": user.id},
                )
                continue

            bookings_to_transfer = _get_bookings_to_transfer(underage_deposit)
            if not bookings_to_transfer:
                continue

            _transfer_bookings(bookings_to_transfer, user)

            if not_dry:
                db.session.flush()
                update_external_user(user)

        from_id += batch_size
        current_page += 1
        logger.info(
            "Processed users up to id %s. %s remaining (%s pages)",
            from_id,
            max_id - from_id,
            estimated_page_number - current_page,
        )


def _get_bookings_to_transfer(deposit: Deposit) -> list[Booking]:
    bookings_to_transfer = []
    for booking in deposit.bookings:
        if booking.stock.offer.subcategory.reimbursement_rule == ReimbursementRuleChoices.NOT_REIMBURSED:
            continue
        if booking.amount == 0:
            continue
        if booking.status in (BookingStatus.CONFIRMED, BookingStatus.USED):
            bookings_to_transfer.append(booking)
        elif booking.status == BookingStatus.CANCELLED:
            # check if it was cancelled after the underage deposit was deactivated (then we also want to transfer it)
            if deposit.expirationDate is None:
                logger.warning(
                    "deposit %s was found without an expiration date", deposit.id, extra={"deposit_id": deposit.id}
                )
                continue
            if booking.cancellationDate is None:
                logger.warning(
                    "cancelled booking %s was found without an cancellation date",
                    booking.id,
                    extra={"booking_id": booking.id},
                )
                continue
            if booking.cancellationDate > deposit.expirationDate:
                bookings_to_transfer.append(booking)

    return bookings_to_transfer


def _transfer_bookings(bookings: list[Booking], user: User) -> None:
    logger.info(
        "Transfering %s bookings for user %s",
        len(bookings),
        user.id,
        extra={"booking_ids": [booking.id for booking in bookings], "user_id": user.id},
    )
    deposit = user.deposit
    if not deposit:
        logger.info("User %s has no deposit", user.id, extra={"user_id": user.id})  # should not happen
        return

    for booking in bookings:
        booking.deposit = deposit
        recredit = Recredit(
            deposit=deposit,
            amount=booking.total_amount,
            recreditType=RecreditType.MANUAL_MODIFICATION,
            comment=f"(PC-36835) Transfert de la réservation {booking.id} qui provient du crédit précédent",
        )
        deposit.amount += recredit.amount


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    parser.add_argument("--from-id", type=int, default=0)
    parser.add_argument("--batch-size", type=int, default=1000)
    args = parser.parse_args()

    main(not_dry=args.not_dry, from_id=args.from_id, batch_size=args.batch_size)

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
