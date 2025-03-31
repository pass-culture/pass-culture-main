"""
https://github.com/pass-culture/pass-culture-main/blob/PC-35423-expire-deposits/api/src/pcapi/scripts/expire_pre_decree_credits/main.py
"""

from argparse import ArgumentParser
from datetime import datetime
import logging

from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import joinedload

from pcapi.app import app
from pcapi.core.external.attributes.api import update_external_user
from pcapi.core.finance.models import Deposit
from pcapi.core.finance.models import DepositType
from pcapi.core.history.models import ActionHistory
from pcapi.core.history.models import ActionType
from pcapi.core.users.models import User
from pcapi.core.users.repository import find_user_by_email
from pcapi.models import db
from pcapi.settings import CREDIT_V3_DECREE_DATETIME


logger = logging.getLogger(__name__)


def expire_deposits(not_dry: bool, last_deposit_id: int = 0) -> None:
    logger.info("starting expire_deposits")

    author = find_user_by_email("dan.nguyen@passculture.app")
    if not author:
        raise ValueError("author account not found")

    while True:
        deposits = _get_deposits_to_expire(last_deposit_id)
        for deposit in deposits:
            _expire_deposit(deposit, author)

            if not_dry:
                db.session.flush()
                update_external_user(deposit.user)

        if not deposits:
            break

        last_deposit_id = deposits[-1].id


def _get_deposits_to_expire(last_deposit_id: int) -> list[Deposit]:
    two_years_before_decree = CREDIT_V3_DECREE_DATETIME - relativedelta(years=2)
    deposits_to_expire = (
        Deposit.query.filter(
            Deposit.type == DepositType.GRANT_18,
            Deposit.dateCreated < two_years_before_decree,
            Deposit.expirationDate >= datetime.utcnow(),
            Deposit.id > last_deposit_id,
        )
        .order_by(Deposit.id)
        .options(joinedload(Deposit.user).load_only(User.id))
        .limit(500)
        .all()
    )

    logger.info("expiring %s deposits", len(deposits_to_expire))
    return deposits_to_expire


def _expire_deposit(deposit: Deposit, author: User) -> None:
    logger.info(
        "expiring deposit %s, that was created on %s",
        deposit.id,
        deposit.dateCreated.isoformat(),
        extra={"user_id": deposit.user.id},
    )

    deposit.expirationDate = deposit.dateCreated + relativedelta(years=2)

    action_history = ActionHistory(
        actionType=ActionType.COMMENT,
        user=deposit.user,
        authorUser=author,
        comment="(PC-35423) Expiration des crédits qui étaient expirés avant le décret",
    )
    db.session.add(action_history)


if __name__ == "__main__":
    app.app_context().push()

    parser = ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    parser.add_argument("--last-deposit-id", type=int, default=0)
    args = parser.parse_args()

    expire_deposits(args.not_dry, args.last_deposit_id)

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
