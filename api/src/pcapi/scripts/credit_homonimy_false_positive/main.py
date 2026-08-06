"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-41661-homonimy-false-positive \
  -f NAMESPACE=credit_homonimy_false_positive \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging
from decimal import Decimal

from sqlalchemy import select

from pcapi.app import app
from pcapi.core.external.attributes.api import update_external_user
from pcapi.core.finance.conf import RECREDIT_TYPE_AMOUNT_MAPPING
from pcapi.core.finance.models import Deposit
from pcapi.core.finance.models import DepositType
from pcapi.core.finance.models import Recredit
from pcapi.core.finance.models import RecreditType
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.utils import date as date_utils
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)

COMMENT_MESSAGE = "(PC-41661) Rattrapage du crédit que le jeune aurait dû avoir s'il n'était pas bloqué par l'homonymie"


def credit_user(user: User) -> None:
    current_deposit = user.deposit
    if not current_deposit:
        raise ValueError("user has no current deposit")

    underage_deposit = Deposit(
        user=user,
        type=DepositType.GRANT_15_17,
        expirationDate=date_utils.get_naive_utc_now(),
        amount=Decimal(0),
        source=COMMENT_MESSAGE,
        version=1,
    )
    sixteen_year_old_recredit = Recredit(
        deposit=underage_deposit,
        recreditType=RecreditType.RECREDIT_16,
        amount=RECREDIT_TYPE_AMOUNT_MAPPING[RecreditType.RECREDIT_16],
        comment=COMMENT_MESSAGE,
    )
    seventeen_year_old_recredit = Recredit(
        deposit=underage_deposit,
        recreditType=RecreditType.RECREDIT_17,
        amount=RECREDIT_TYPE_AMOUNT_MAPPING[RecreditType.RECREDIT_17],
        comment=COMMENT_MESSAGE,
    )
    underage_deposit.amount += sixteen_year_old_recredit.amount
    underage_deposit.amount += seventeen_year_old_recredit.amount

    previous_deposit_recredit = Recredit(
        deposit=current_deposit,
        amount=underage_deposit.amount,
        recreditType=RecreditType.PREVIOUS_DEPOSIT,
        comment=COMMENT_MESSAGE,
    )
    current_deposit.amount += previous_deposit_recredit.amount

    db.session.add_all(
        [underage_deposit, sixteen_year_old_recredit, seventeen_year_old_recredit, previous_deposit_recredit]
    )
    db.session.flush()

    logger.info(
        "recredited user %s",
        user.id,
        extra={"user_id": user.id, "deposit_type": current_deposit.type, "deposit_amount": current_deposit.amount},
    )


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--user-id", type=int)
    args = parser.parse_args()

    with atomic():
        user = db.session.scalars(select(User).where(User.id == args.user_id)).one()

        credit_user(user)

        if args.apply:
            update_external_user(user)
            logger.info("finished")
        else:
            mark_transaction_as_invalid()
            logger.info("dry run, rollbacking")
