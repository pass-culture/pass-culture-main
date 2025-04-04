"""
https://github.com/pass-culture/pass-culture-main/blob/PC-34930-300-euros-for-the-deserving/api/src/pcapi/scripts/finance/main.py
"""

import argparse
from decimal import Decimal
import logging

from sqlalchemy import text
from sqlalchemy.orm import selectinload

from pcapi.app import app
from pcapi.core.external.attributes.api import update_external_user
from pcapi.core.finance.models import Deposit
from pcapi.core.finance.models import DepositType
from pcapi.core.finance.models import Recredit
from pcapi.core.finance.models import RecreditType
from pcapi.core.fraud.models import BeneficiaryFraudCheck
from pcapi.core.fraud.models import FraudCheckStatus
from pcapi.core.users.models import EligibilityType
from pcapi.core.users.models import User
from pcapi.core.users.utils import get_age_at_date
from pcapi.models import db


logger = logging.getLogger(__name__)


def fix_pre_decree_deposit_amount(not_dry: bool, last_user_id: int = 0) -> None:
    logger.info("starting fix_pre_decree_deposit_amount")

    while True:
        users = _get_users_that_should_have_300_euros(last_user_id)
        if not users:
            break

        users_to_recredit = list(filter(_was_18_at_any_fraud_check, users))
        if users_to_recredit:
            logger.info("received %s users to recredit", len(users_to_recredit))

        for user in users_to_recredit:
            deposit = user.deposit
            if not deposit or deposit.type != DepositType.GRANT_17_18:
                continue

            has_been_recredited_for_eighteen = any(
                recredit.recreditType == RecreditType.RECREDIT_18 for recredit in deposit.recredits
            )
            if not has_been_recredited_for_eighteen:
                continue

            _recredit_deposit(deposit)

            if not_dry:
                db.session.flush()
                update_external_user(user)

        last_user_id = users[-1].id


def _get_users_that_should_have_300_euros(last_user_id: int) -> list[User]:
    return (
        User.query.join(User.deposits)
        .filter(
            BeneficiaryFraudCheck.query.filter(
                BeneficiaryFraudCheck.userId == User.id,
                BeneficiaryFraudCheck.eligibilityType == EligibilityType.AGE18,
                BeneficiaryFraudCheck.status == FraudCheckStatus.OK,
            ).exists(),
        )
        .filter(
            Deposit.type == DepositType.GRANT_17_18,
            Deposit.amount < 300,
            Deposit.recredits.any(Recredit.recreditType == RecreditType.RECREDIT_18),
        )
        .filter(User.id > last_user_id)
        .order_by(User.id)
        .options(selectinload(User.deposits).selectinload(Deposit.recredits))
        .options(selectinload(User.beneficiaryFraudChecks))
        .limit(500)
        .all()
    )


def _was_18_at_any_fraud_check(user: User) -> bool:
    age_18_fraud_checks = [
        fraud_check
        for fraud_check in user.beneficiaryFraudChecks
        if fraud_check.eligibilityType == EligibilityType.AGE18 and fraud_check.status == FraudCheckStatus.OK
    ]

    return any(
        [
            18 <= get_age_at_date(user.birth_date, fraud_check.dateCreated, user.departementCode) <= 19
            for fraud_check in age_18_fraud_checks
        ]
    )


def _recredit_deposit(deposit: Deposit) -> None:
    amount_to_recredit = Decimal("300") - deposit.amount
    recredit = Recredit(
        deposit=deposit,
        amount=amount_to_recredit,
        recreditType=RecreditType.MANUAL_MODIFICATION,
        comment="(PC-35309) Rattrapage des 18 ans pré-décret qui n'ont pas eu 300€",
    )
    deposit.amount += recredit.amount

    logger.info(
        "Recredited user %s on deposit %s created on %s", deposit.user.id, deposit.id, deposit.dateCreated.isoformat()
    )


if __name__ == "__main__":
    app.app_context().push()
    db.session.execute(text("set session statement_timeout = '500s'"))

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    parser.add_argument("--last-user-id", type=int, default=0)
    args = parser.parse_args()

    fix_pre_decree_deposit_amount(args.not_dry, args.last_user_id)

    if args.not_dry:
        db.session.commit()
        logger.info("Pre decree deposit amounts fixed and committed")
    else:
        db.session.rollback()
        logger.info("Dry run and rollback completed")
