"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-40800-support-actions \
  -f NAMESPACE=extend_deposit \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import csv
import logging
import os
from datetime import datetime
from typing import Sequence

from sqlalchemy import select

from pcapi.app import app
from pcapi.core.external.attributes.api import update_external_user
from pcapi.core.history.models import ActionHistory
from pcapi.core.history.models import ActionType
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)
namespace_dir = os.path.dirname(os.path.abspath(__file__))

FILE_NAME = "users_to_extend_credit.csv"


def extend_deposit(user: User, expiration_date: datetime, author_id: int | None = None) -> None:
    deposit = user.deposit
    if not deposit:
        logger.error("no deposit was found", extra={"user_id": user.id})
        return

    deposit.expirationDate = expiration_date

    action_history = ActionHistory(
        user=user,
        actionType=ActionType.COMMENT,
        authorUserId=author_id,
        comment=f"(PC-40800) Extension du crédit jusqu'au {expiration_date.date().isoformat()} parce que du crédit n'a pas pu être dépensé à cause d'un incident technique",
    )
    db.session.add(action_history)

    logger.info(
        "Extended deposit",
        extra={"user_id": user.id, "deposit_id": deposit.id, "expiration_date": expiration_date},
    )


def read_users_from_csv(file_name: str) -> Sequence[User]:
    with open(f"{namespace_dir}/{file_name}", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        return db.session.scalars(select(User).where(User.id.in_([row["user_id"] for row in reader]))).all()


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--author-id", type=int, default=None)
    parser.add_argument("--expiration-date", type=datetime.fromisoformat)
    args = parser.parse_args()

    with atomic():
        if not args.apply:
            mark_transaction_as_invalid()
            logger.info("dry run, rollbacking at the end of the transaction")

        for user in read_users_from_csv(FILE_NAME):
            extend_deposit(user, args.expiration_date, args.author_id)

            if args.apply:
                update_external_user(user)
