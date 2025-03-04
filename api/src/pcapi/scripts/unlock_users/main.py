import argparse
import logging

from pcapi.app import app
from pcapi.core.finance.enum import DepositType
from pcapi.core.finance.models import Deposit
from pcapi.core.finance.models import Recredit
from pcapi.core.finance.models import RecreditType
from pcapi.models import db


logger = logging.getLogger(__name__)

app.app_context().push()


def main() -> None:
    query = (
        db.session.query(Deposit)
        .join(Deposit.recredits)
        .filter(
            Deposit.type == DepositType.GRANT_15_17,
            Recredit.recreditType == RecreditType.RECREDIT_18,
        )
    )

    for deposit in query:
        user = deposit.user
        # This user has been credited a 18yo amount on a 15_17 deposit
        # - Remove the 18yo recredit
        # - Remove the amount on the active deposit if it was transferred
        current_deposit = user.deposit
        user_underage_deposits = [deposit for deposit in user.deposits if deposit.type == DepositType.GRANT_15_17]
        latest_underage_deposit = user_underage_deposits[0] if user_underage_deposits else None

        if not latest_underage_deposit:
            # cannot happen with the query above
            logger.error("User %s has no underage deposit", user.id)
            continue

        if current_deposit.id == latest_underage_deposit.id:
            # The user has been credited a 18yo amount on a 15_17 deposit
            # Remove the 18yo recredit
            recredit = Recredit.query.filter(
                Recredit.deposit == latest_underage_deposit, Recredit.recreditType == RecreditType.RECREDIT_18
            ).one_or_none()
            if recredit:
                amount_to_remove = recredit.amount
                current_deposit.amount -= amount_to_remove
                db.session.add(current_deposit)
                db.session.delete(recredit)
                db.session.flush()
                logger.info("Removed recredit %s for user %s", recredit.id, user.id)

        else:
            # The user has been credited a 18yo amount on a 15_17 deposit, and then transferred the amount to a 18yo deposit
            if not current_deposit.type in (DepositType.GRANT_18, DepositType.GRANT_17_18):
                # cannot happen with the query above
                logger.error("User %s has a deposit of type %s", user.id, current_deposit.type)
                continue

            # Find the RECREDIT_18 on the underage deposit
            recredit_18_on_underage = Recredit.query.filter(
                Recredit.deposit == latest_underage_deposit, Recredit.recreditType == RecreditType.RECREDIT_18
            ).one_or_none()
            if not recredit_18_on_underage:
                # cannot happen with the query above
                logger.error("User %s has no RECREDIT_18 on the underage deposit", user.id)
                continue
            amount_to_remove = recredit_18_on_underage.amount

            # Check the 18yo deposit has already a RECREDIT_18 ; and has the credit trasfered.
            recredit_18_on_current_deposit = [
                recredit for recredit in current_deposit.recredits if recredit.recreditType == RecreditType.RECREDIT_18
            ]
            recredit_transferred = [
                recredit
                for recredit in current_deposit.recredits
                if recredit.recreditType == RecreditType.PREVIOUS_DEPOSIT
            ]
            if not recredit_18_on_current_deposit or not recredit_transferred:
                # Should not happen. If it does, do nothing.
                logger.info("Non problematic case for user %s", user.id)
                continue

            # Remove the 18yo recredit
            db.session.delete(recredit_18_on_underage)
            current_deposit.amount -= amount_to_remove
            recredit_transferred[0].amount -= amount_to_remove
            logger.info(
                "Removed recredit %s for user %s (amount %s)", recredit_18_on_underage.id, user.id, amount_to_remove
            )

        print("Bilan")
        print("User", user.id)
        for d in user.deposits:
            print("Deposit", d.id, d.type, d.amount)
            for r in d.recredits:
                print("Recredit", r.id, r.recreditType, r.amount)


if __name__ == "__main__":
    # https://github.com/pass-culture/pass-culture-main/blob/pc-34907/api/src/pcapi/scripts/unlock_users/main.py
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
