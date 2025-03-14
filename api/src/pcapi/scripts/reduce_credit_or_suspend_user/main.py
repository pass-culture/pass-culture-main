from argparse import ArgumentParser
from decimal import Decimal
import logging

from sqlalchemy.orm import Query
from sqlalchemy.orm import joinedload

from pcapi.app import app
from pcapi.core.finance.conf import GRANTED_DEPOSIT_AMOUNT_18_v3
from pcapi.core.finance.models import RecreditType
from pcapi.core.history.models import ActionHistory
from pcapi.core.history.models import ActionType
from pcapi.core.users.api import get_domains_credit
from pcapi.core.users.api import suspend_account
from pcapi.core.users.constants import SuspensionReason
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.repository import transaction


logger = logging.getLogger(__name__)


def reduce_credit_or_suspend_user(is_not_dry_run: bool) -> None:
    logger.info("starting reduce_credit_or_suspend_user")

    deposits_query = Deposit.query.filter(
        # select id from deposit where deposit."dateCreated" > '2025-03-03' order by id limit 1;
        Deposit.id > 6362356,
        Deposit.amount == 450,
    ).options(joinedload(Deposit.user))
    for deposit in deposits_query.yield_per(1000):
        user = deposit.user
        domains_credit = get_domains_credit(user)
        if not domains_credit:
            logger.warning("no domains credit found for user %s", user.id)
            continue

        if domains_credit.all.initial != Decimal("450"):
            logger.warning("user %s does not have 450 € but %s €", domains_credit.all.initial)
            continue

        can_reduce_credit = domains_credit.all.remaining >= GRANTED_DEPOSIT_AMOUNT_18_v3
        if can_reduce_credit:
            logger.info("reducing credit of user %s, on deposit %s", user.id, deposit.id)
            _reduce_credit(user, is_not_dry_run)
        else:
            logger.info(
                "cannot reduce user %s credit because only %s € is left, suspending user instead",
                user.id,
                domains_credit.all.remaining,
            )
            _suspend_user(user, is_not_dry_run)


def _reduce_credit(user: User, is_not_dry_run: bool) -> None:
    deposit = user.deposit
    if not deposit:
        logger.warning("deposit mysteriously disappeared for user %s", user.id)
        return

    age_18_recredit = next(
        (recredit for recredit in deposit.recredits if recredit.recreditType == RecreditType.RECREDIT_18), None
    )
    if age_18_recredit:
        logger.warning("deposit %s of user %s does not have the 18 recredit", deposit.id, user.id)
        return

    if not is_not_dry_run:
        return

    with transaction():
        deposit.amount -= age_18_recredit.amount
        db.session.delete(age_18_recredit)

        action_log = ActionHistory(
            actionType=ActionType.FRAUD_INFO_MODIFIED,
            user=user,
            authorUserId=1633706,  # thanks cnormant-pass
            comment="(PC-35179) Retrait du crédit de 150€ donné par erreur sur un crédit de 300€",
        )
        db.session.add(action_log)

    logger.info("reduced credit of user %s, on deposit %s", user.id, deposit.id)


def _suspend_user(user: User, is_not_dry_run: bool) -> None:
    if not is_not_dry_run:
        return

    suspend_account(
        user,
        reason=SuspensionReason.FRAUD_SUSPICION,
        comment="(PC-35179) Retrait du crédit de 150€ impossible, donné par erreur sur un crédit de 300€",
        actor=None,
    )

    logger.info("suspended user %s", user.id)


if __name__ == "__main__":
    app.app_context().push()

    parser = ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    reduce_credit_or_suspend_user(args.not_dry)
