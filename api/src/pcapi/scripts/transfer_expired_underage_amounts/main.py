import argparse
from decimal import Decimal
import logging

from pcapi.app import app
from pcapi.core.bookings.repository import get_bookings_from_deposit
from pcapi.core.external.attributes.api import update_external_user
from pcapi.core.finance.api import _recredit_deposit
from pcapi.core.finance.enum import DepositType  # for staging

# from pcapi.core.finance.models import DepositType
from pcapi.core.finance.models import Deposit
from pcapi.core.finance.models import RecreditType
from pcapi.core.users.api import _get_booking_credit
from pcapi.core.users.models import User
from pcapi.models import db


logger = logging.getLogger(__name__)


def transfer_expired_underage_amounts(from_id: int, batch_size: int) -> None:
    # Find users with:
    # - deposits 17_18 with amount 150
    # - deposits 15_17
    query = (
        User.query.join(User.deposits)
        .filter(
            User.deposits.any(type=DepositType.GRANT_17_18, amount=150),
            User.deposits.any(type=DepositType.GRANT_15_17),
        )
        .order_by(User.id.desc())
    )
    latest_user = query.first()
    if not latest_user:
        logger.info("No user to process")
        return

    max_id = latest_user.id

    while from_id < max_id:
        logger.info("Processing users from id %s to id %s", from_id, from_id + batch_size)
        for user in query.filter(User.id > from_id, User.id <= from_id + batch_size):
            current_deposit = user.deposit
            if current_deposit.type != DepositType.GRANT_17_18:
                continue
            if current_deposit.amount != 150:
                continue

            try:
                underage_deposit = [deposit for deposit in user.deposits if deposit.type == DepositType.GRANT_15_17][0]
            except IndexError:
                logger.info("No underage deposit for user %s", user.id)
                continue
            if not underage_deposit:
                continue

            if current_deposit.id == underage_deposit.id:
                continue

            if any(recredit.recreditType == RecreditType.PREVIOUS_DEPOSIT for recredit in current_deposit.recredits):
                logger.info("Skipping deposit %s, it has a previous deposit recredit", current_deposit.id)
                continue

            remaining_amount = _get_remaining_credit(underage_deposit)
            if not remaining_amount:
                logger.info("No amount remaining in deposit %s", underage_deposit.id)
                continue
            logger.info(
                "Transferring remaining amount %s from deposit %s to deposit %s",
                remaining_amount,
                underage_deposit.id,
                current_deposit.id,
            )
            _recredit_deposit(current_deposit, 18, RecreditType.PREVIOUS_DEPOSIT, remaining_amount)  # flushes
            try:
                update_external_user(user)
            except Exception as e:  # pylint: disable=broad-except
                logger.error("Error while updating attributes for user %s: %s", user.id, e)
        from_id += batch_size
        logger.info("Done. New max id: %s", from_id)
        logger.info("Progress: %s%%", round((from_id / max_id) * 100))


def _get_remaining_credit(deposit: Deposit) -> Decimal:
    deposit_bookings = get_bookings_from_deposit(deposit.id)

    return max(
        deposit.amount - sum(_get_booking_credit(booking) for booking in deposit_bookings),
        Decimal("0"),
    )


if __name__ == "__main__":
    app.app_context().push()
    # https://github.com/pass-culture/pass-culture-main/blob/pc-34983-script/api/src/pcapi/scripts/transfer_expired_underage_amounts/main.py

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    parser.add_argument("--from-id", type=int, default=0)
    parser.add_argument("--batch-size", type=int, default=1000)
    args = parser.parse_args()

    transfer_expired_underage_amounts(from_id=args.from_id, batch_size=args.batch_size)

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
