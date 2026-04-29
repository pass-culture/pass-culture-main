"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-41300-recredit-user \
  -f NAMESPACE=recredit_user \
  -f SCRIPT_ARGUMENTS="--user-id 8529522 --apply";

"""

import argparse
import logging
from decimal import Decimal

from sqlalchemy import select

from pcapi.app import app
from pcapi.core.finance.models import Recredit
from pcapi.core.finance.models import RecreditType
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)


def recredit_user_for_17_yo(user: User) -> None:
    deposit = user.deposit
    if not deposit:
        raise ValueError(f"missing deposit for user {user.id}")

    recredit = Recredit(
        deposit=deposit,
        amount=Decimal("50"),
        recreditType=RecreditType.RECREDIT_17,
        comment="(PC-41300) Le jeune s'étant inscrit à 16 ans, il aurait dû avoir les crédits de ses 17 ans",
    )
    deposit.amount += recredit.amount

    db.session.add(recredit)
    db.session.flush()

    logger.info("recredited user", extra={"user_id": user.id})


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--user-id", type=int)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    with atomic():
        if not args.apply:
            logger.info("dry run")
            mark_transaction_as_invalid()

        user_stmt = select(User).where(User.id == args.user_id)
        user = db.session.scalars(user_stmt).one()
        recredit_user_for_17_yo(user)
