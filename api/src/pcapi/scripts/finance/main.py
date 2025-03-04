import argparse
from decimal import Decimal
import logging

from sqlalchemy.orm import selectinload

from pcapi.app import app
from pcapi.core.finance.enum import DepositType
from pcapi.core.finance.models import Deposit
from pcapi.core.finance.models import Recredit
from pcapi.core.finance.models import RecreditType
from pcapi.core.fraud.models import BeneficiaryFraudCheck
from pcapi.core.users.models import EligibilityType
from pcapi.core.users.models import User
from pcapi.models import db


logger = logging.getLogger(__name__)


def fix_pre_decree_deposit_amount() -> None:
    users = (
        User.query.join(User.deposits)
        .filter(
            BeneficiaryFraudCheck.query.filter(
                BeneficiaryFraudCheck.userId == User.id, BeneficiaryFraudCheck.eligibilityType == EligibilityType.AGE18
            ).exists(),
        )
        .filter(
            Deposit.type == DepositType.GRANT_17_18,
            Recredit.query.filter(
                Recredit.depositId == Deposit.id, Recredit.recreditType == RecreditType.RECREDIT_18
            ).exists(),
        )
        .options(selectinload(User.deposits))
        .all()
    )

    for user in users:
        deposit = user.deposit
        if deposit.type != DepositType.GRANT_17_18:
            continue

        amount_to_recredit = Decimal("300") - deposit.amount
        recredit = Recredit(
            deposit=deposit,
            amount=amount_to_recredit,
            recreditType=RecreditType.MANUAL_MODIFICATION,
            comment="(PC-34930) Rattrapage des 18 ans pré-décret qui n'ont pas eu 300€",
        )
        deposit.amount += recredit.amount

        logger.info("Recredited user %s on deposit %s", user.id, deposit.id)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    fix_pre_decree_deposit_amount()

    if args.dry_run:
        db.session.rollback()
        logger.info("Dry run and rollback completed")
    else:
        db.session.commit()
        logger.info("Pre decree deposit amounts fixed and committed")
