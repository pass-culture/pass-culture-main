"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions): 

https://github.com/pass-culture/pass-culture-main/blob/pc-35266-transfer-cancellable-bookings-to-new-deposit-script/api/src/pcapi/scripts/transfer_bookings_to_new_deposits/main.py

"""

import argparse
import logging
import math

from pcapi.app import app
from pcapi.core.bookings.models import Booking
from pcapi.core.categories.models import ReimbursementRuleChoices
from pcapi.core.external.attributes.api import update_external_user
from pcapi.core.finance.models import Deposit
from pcapi.core.finance.models import DepositType
from pcapi.core.users.models import User
from pcapi.models import db


logger = logging.getLogger(__name__)


def main(not_dry: bool, from_id: int, batch_size: int) -> None:
    query = User.query.filter(
        User.deposits.any(Deposit.type == DepositType.GRANT_17_18),
        User.deposits.any(Deposit.type == DepositType.GRANT_15_17),
        User.id > from_id,
    ).order_by(User.id)

    max_id = query.first().id
    pages = math.ceil(max_id / batch_size)
    current_page = 1
    logger.info("Max id = %s", max_id)

    while from_id <= max_id:
        logger.info("Processing users from id %s to %s", from_id, from_id + batch_size)
        for user in query.filter(User.id > from_id, User.id <= from_id + batch_size).all():
            underage_deposit = next(deposit for deposit in user.deposits if deposit.type == DepositType.GRANT_15_17)

            if not underage_deposit:
                logger.info("User %s has no underage deposit", user.id)  # should not happen
                continue

            if user.deposit.id == underage_deposit.id:
                logger.info("User %s has an underage deposit as its active one. Skipping.", user.id)
                continue

            bookings_to_transfer = []
            for booking in underage_deposit:
                if booking.stock.offer.subcategory.reimbursement_rule == ReimbursementRuleChoices.NOT_REIMBURSED:
                    continue
                if booking.status in (Booking.Status.CONFIRMED, Booking.Status.USED):
                    bookings_to_transfer.append(booking)
                elif booking.status == Booking.Status.CANCELLED:
                    # check if it was cancelled after the underage deposit was deactivated (then we also want to transfer it)
                    if booking.cancellationDate > underage_deposit.expirationDate:
                        bookings_to_transfer.append(booking)

            # transfer bookings
            logger.info(
                "Transfering %s bookings for user %s",
                len(bookings_to_transfer),
                user.id,
                extra={"booking_ids": [booking.id for booking in bookings_to_transfer]},
            )
            for booking in bookings_to_transfer:
                booking.deposit = user.deposit
                user.deposit.amount += booking.total_amount

            if not_dry:
                update_external_user(user)

        from_id += batch_size
        current_page += 1
        logger.info(
            "Processed users up to id %s. %s remaining (%s pages)", from_id, max_id - from_id, pages - current_page
        )


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
