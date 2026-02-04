"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=stg \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-40139-unexpire-credits \
  -f NAMESPACE=unexpire_credits \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import csv
import logging
import os
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from pcapi.app import app
from pcapi.core.external.attributes.api import update_external_user
from pcapi.core.finance.conf import GRANTED_DEPOSIT_AMOUNT_17_v3
from pcapi.core.finance.deposit_api import compute_deposit_expiration_date
from pcapi.core.finance.models import Recredit
from pcapi.core.finance.models import RecreditType
from pcapi.core.history.models import ActionHistory
from pcapi.core.history.models import ActionType
from pcapi.core.users.api import get_domains_credit
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


namespace_dir = os.path.dirname(os.path.abspath(__file__))
logger = logging.getLogger(__name__)


def reduce_credit_instead_of_expiring_credits(
    users: list[User], author_id: int, should_update_external_user: bool = False
) -> None:
    for user in users:
        deposit = user.deposit
        if not deposit:
            logger.error("deposit not found on user %d", user.id)
            mark_transaction_as_invalid()
            continue

        if not deposit.expirationDate or deposit.expirationDate >= datetime.now(tz=None):
            logger.error("deposit %d of user %d has invalid expiration date")
            mark_transaction_as_invalid()
            continue

        deposit.expirationDate = compute_deposit_expiration_date(user)
        action_log = ActionHistory(
            actionType=ActionType.COMMENT,
            user=user,
            authorUserId=author_id,
            comment="(PC-40139) Extension du crédit pour que le jeune puisse réserver des offres gratuites",
        )
        db.session.add(action_log)
        logger.info("extended deposit %d expiration date", deposit.id)

        domains_credit = get_domains_credit(user)
        if not domains_credit:
            logger.error("deposit not found on user %d", user.id)
            mark_transaction_as_invalid()
            continue

        amount_to_reverse = min(domains_credit.all.remaining, GRANTED_DEPOSIT_AMOUNT_17_v3)
        if amount_to_reverse == GRANTED_DEPOSIT_AMOUNT_17_v3:
            operation_comment = "(PC-40139) Retrait du crédit 17 ans donné par erreur"
        else:
            operation_comment = "(PC-40139) Retrait du crédit restant parce que le jeune a consommé un surplus de crédit donné par erreur"

        reverse_amount = -amount_to_reverse
        if reverse_amount > 0:
            logger.error("user %d has zero or negative remaining credit", user.id)
            mark_transaction_as_invalid()
            continue

        reverse_recredit = Recredit(
            deposit=deposit,
            amount=reverse_amount,
            recreditType=RecreditType.MANUAL_MODIFICATION,
            comment=operation_comment,
        )
        deposit.amount += reverse_recredit.amount
        db.session.add(reverse_recredit)
        logger.info(
            "user %d deposit %d reduced",
            user.id,
            deposit.id,
            extra={"user_id": user.id, "amount": amount_to_reverse},
        )

        if should_update_external_user:
            update_external_user(user)


def read_users_from_csv(file_name: str) -> list[User]:
    with open(file_name, encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)

        user_ids = [int(row["user_id"]) for row in reader]

    users_stmt = select(User).where(User.id.in_(user_ids)).options(selectinload(User.deposits))

    return list(db.session.scalars(users_stmt).all())


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    parser.add_argument("--author-id", type=int)
    args = parser.parse_args()

    logger.info("starting")

    with atomic():
        if not args.not_dry:
            logger.info("Dry run enabled, rollbacking at the end of the atomic block")
            mark_transaction_as_invalid()

        users = read_users_from_csv(f"{namespace_dir}/id_beneficiaires_credit_expire.csv")
        reduce_credit_instead_of_expiring_credits(users, args.author_id, should_update_external_user=args.not_dry)

    logger.info("finished")
