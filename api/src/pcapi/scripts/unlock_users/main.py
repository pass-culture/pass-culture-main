import argparse
import logging

from pcapi.app import app
from pcapi.core.finance.enum import DepositType
from pcapi.core.finance.models import Deposit
from pcapi.core.subscription.api import activate_beneficiary_if_no_missing_step
from pcapi.core.users.models import User
from pcapi.models import db


logger = logging.getLogger(__name__)

app.app_context().push()


def main(not_dry: bool) -> None:
    query = (
        db.session.query(User)
        .join(User.deposits)
        .filter(
            User.has_beneficiary_role,
            Deposit.type == DepositType.GRANT_15_17,
            Deposit.expirationDate > db.func.now(),
        )
    )
    users_to_update = query.all()
    logger.info("Found %s users to update", len(users_to_update))
    for user in users_to_update:
        logger.info("Updating user %s", user.id)
        user.remove_beneficiary_role()
        if user.deposit and user.deposit.type == DepositType.GRANT_15_17:
            user.add_underage_beneficiary_role()
        db.session.add(user)

        if not_dry:
            try:
                activate_beneficiary_if_no_missing_step(user)
            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.info("Error while trying to activate user %s: %s", user.id, e)


if __name__ == "__main__":
    # https://github.com/pass-culture/pass-culture-main/blob/pc-34907/api/src/pcapi/scripts/unlock_users/main.py
    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    main(not_dry=args.not_dry)

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
