"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml   -f ENVIRONMENT=testing   -f BRANCH_NAME=PC-38528-transfer-credit-through-accounts   -f NAMESPACE=transfer_credit   -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from pcapi.app import app
from pcapi.core.finance.models import Recredit
from pcapi.core.finance.models import RecreditType
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic


logger = logging.getLogger(__name__)


def transfer_credit(from_user_id: int, to_user_id: int) -> None:
    from_stmt = select(User).where(User.id == from_user_id).options(selectinload(User.deposits))
    from_user = db.session.scalars(from_stmt).one()
    from_deposit = from_user.deposit
    assert from_deposit, f"{from_user = } does not have a deposit"

    to_stmt = select(User).where(User.id == to_user_id).options(selectinload(User.deposits))
    to_user = db.session.scalars(to_stmt).one()
    to_deposit = to_user.deposit
    assert to_deposit, f"{to_user = } does not have a deposit"

    recredit = Recredit(
        deposit=to_deposit,
        amount=from_deposit.amount,
        recreditType=RecreditType.MANUAL_MODIFICATION,
        comment=f"(PC-38528) Transfert du crédit de l'utilisateur {from_user.id} vers l'utilisateur {to_user.id}",
    )
    to_deposit.amount += recredit.amount

    db.session.add(recredit)

    logger.info(f"Recredited {recredit.amount} euros {to_user = }")


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--from-user-id", type=int, default=3962434)
    parser.add_argument("--to-user-id", type=int, default=6885227)
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    with atomic():
        transfer_credit(args.from_user_id, args.to_user_id)

        if not args.not_dry:
            logger.info("Finished dry run, rollback")
            db.session.rollback()
        else:
            logger.info("Finished")
