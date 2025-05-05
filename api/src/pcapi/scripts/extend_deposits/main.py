"""
https://github.com/pass-culture/pass-culture-main/blob/PC-35758-extend-deposits/api/src/pcapi/scripts/extend_deposits/main.py
"""

import argparse
from datetime import date
import logging

from dateutil.relativedelta import relativedelta
from sqlalchemy import text
from sqlalchemy.orm import selectinload

from pcapi.app import app
from pcapi.core.external.attributes.api import update_external_user
from pcapi.core.finance.models import Deposit
from pcapi.core.finance.models import DepositType
from pcapi.core.history.models import ActionHistory
from pcapi.core.history.models import ActionType
from pcapi.core.subscription.machines import SubscriptionStates
from pcapi.core.subscription.machines import create_state_machine_to_current_state
from pcapi.core.users.models import User
from pcapi.models import db


logger = logging.getLogger(__name__)


AUTHOR_ID = 6721024


def extend_users_deposit(not_dry: bool, last_user_id: int = 0) -> None:
    has_next_page = True
    while has_next_page:
        users = _get_beneficiaries_to_extend_deposits(last_user_id)

        users_to_extend_deposit = [user for user in users if _should_extend_deposit(user)]
        if users_to_extend_deposit:
            for user in users_to_extend_deposit:
                _extend_user_deposit(user, should_update_external_user=not_dry)

            if not_dry:
                logger.info("Finished page")
                db.session.commit()
            else:
                logger.info("Finished page dry run, rollback")
                db.session.rollback()

        has_next_page = bool(users)
        if has_next_page:
            last_user_id = users[-1].id


def _get_beneficiaries_to_extend_deposits(last_user_id: int) -> list[User]:
    twenty_one_years_ago = date.today() - relativedelta(years=21)
    return (
        db.session.query(User)
        .filter(
            User.isActive.is_(True),
            User.is_beneficiary,
            User.validatedBirthDate > twenty_one_years_ago,
            User.id > last_user_id,
        )
        .options(selectinload(User.deposits), selectinload(User.beneficiaryFraudChecks))
        .order_by(User.id)
        .limit(2000)
        .all()
    )


def _should_extend_deposit(user: User) -> bool:
    deposit = user.deposit
    if deposit is None:
        return False
    if deposit.type == DepositType.GRANT_18:
        return False
    if deposit.expirationDate is None:
        return False

    if user.birth_date is None:
        return False

    date_when_user_will_be_21 = user.birth_date + relativedelta(years=21, hours=11)
    if deposit.expirationDate.date() == date_when_user_will_be_21.date():
        return False

    subscription_state_machine = create_state_machine_to_current_state(user)
    if subscription_state_machine.state not in [SubscriptionStates.BENEFICIARY, SubscriptionStates.EX_BENEFICIARY]:
        return False

    return True


def _extend_user_deposit(user: User, should_update_external_user: bool) -> None:
    deposit = user.deposit
    if deposit is None or user.birth_date is None:
        return

    date_when_user_will_be_21 = user.birth_date + relativedelta(years=21, hours=11)
    deposit.expirationDate = date_when_user_will_be_21
    logger.info(f"{deposit = } of {user = } was extended", extra={"user_id": user.id, "deposit_id": deposit.id})

    action_log = ActionHistory(
        actionType=ActionType.COMMENT,
        user=user,
        authorUserId=AUTHOR_ID,
        comment=f"(PC-35758) Prolongation de la date d'expiration du crédit {deposit.id}",
    )
    db.session.add(action_log)

    if should_update_external_user:
        update_external_user(user)


if __name__ == "__main__":
    app.app_context().push()
    db.session.execute(text("set session statement_timeout = '500s'"))

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    parser.add_argument("--last_user_id", type=int, default=300_000)
    args = parser.parse_args()

    extend_users_deposit(not_dry=args.not_dry, last_user_id=args.last_user_id)
