"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-40183-false-positive-homonimy \
  -f NAMESPACE=credit_user \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging
from datetime import datetime
from decimal import Decimal

from sqlalchemy import select

from pcapi.app import app
from pcapi.core.external.attributes.api import update_external_user
from pcapi.core.finance.conf import RECREDIT_TYPE_AMOUNT_MAPPING
from pcapi.core.finance.conf import GRANTED_DEPOSIT_AMOUNT_18_v3
from pcapi.core.finance.deposit_api import compute_deposit_expiration_date
from pcapi.core.finance.models import Deposit
from pcapi.core.finance.models import DepositType
from pcapi.core.finance.models import Recredit
from pcapi.core.finance.models import RecreditType
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)

COMMENT_MESSAGE = "(PC-40183) Rattrapage du crédit que le jeune aurait dû avoir s'il n'était pas bloqué par l'homonymie"


def credit_user(user: User) -> None:
    underage_deposit = Deposit(
        user=user,
        type=DepositType.GRANT_15_17,
        expirationDate=datetime.now(tz=None),
        amount=Decimal("0"),
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

    db.session.add_all([underage_deposit, sixteen_year_old_recredit, seventeen_year_old_recredit])
    db.session.flush()

    deposit = Deposit(
        version=1,
        type=DepositType.GRANT_17_18,
        amount=Decimal("0"),
        source=COMMENT_MESSAGE,
        user=user,
        expirationDate=compute_deposit_expiration_date(user),
    )
    previous_deposit_recredit = Recredit(
        deposit=deposit,
        amount=underage_deposit.amount,
        recreditType=RecreditType.PREVIOUS_DEPOSIT,
        comment=COMMENT_MESSAGE,
    )
    eighteen_year_old_recredit = Recredit(
        deposit=deposit,
        amount=GRANTED_DEPOSIT_AMOUNT_18_v3,
        recreditType=RecreditType.RECREDIT_18,
        comment=COMMENT_MESSAGE,
    )
    deposit.amount += previous_deposit_recredit.amount
    deposit.amount += eighteen_year_old_recredit.amount

    db.session.add_all([deposit, previous_deposit_recredit, eighteen_year_old_recredit])
    db.session.flush()

    user.add_beneficiary_role()

    logger.info(
        "credited and activated user",
        extra={"user_id": user.id, "deposit_type": deposit.type, "deposit_amount": deposit.amount},
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
