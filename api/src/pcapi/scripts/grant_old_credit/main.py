"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml   -f ENVIRONMENT=testing   -f BRANCH_NAME=PC-38526-recredit-to-300e   -f NAMESPACE=recredit_user   -f SCRIPT_ARGUMENTS="";
"""

import argparse
import logging
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from pcapi.app import app
from pcapi.core.finance.models import Recredit
from pcapi.core.finance.models import RecreditType
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic


logger = logging.getLogger(__name__)


def recredit_user(user_id: int) -> None:
    stmt = select(User).where(User.id == user_id).options(selectinload(User.deposits))
    user = db.session.scalars(stmt).one()

    deposit = user.deposit
    assert deposit, f"{user = } does not have a deposit"

    amount_to_recredit = Decimal("300") - deposit.amount
    recredit = Recredit(
        deposit=user.deposit,
        amount=amount_to_recredit,
        recreditType=RecreditType.MANUAL_MODIFICATION,
        comment="(PC-38529) Alignement du crédit à la quantité pré-décret",
    )
    deposit.amount += recredit.amount

    db.session.add(recredit)

    logger.info(f"Recredited {recredit.amount} euros to {user = }")


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--user-id", type=int, default=6643865)
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    with atomic():
        recredit_user(user_id=args.user_id)

        if not args.not_dry:
            logger.info("Finished dry run, rollback")
            db.session.rollback()
        else:
            logger.info("Finished")
