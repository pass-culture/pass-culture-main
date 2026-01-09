"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-39377-manual-credit-operations \
  -f NAMESPACE=two_credits_manipulation \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

from sqlalchemy import select

from pcapi.app import app
from pcapi.core.external.attributes.api import update_external_user
from pcapi.core.finance.conf import GRANTED_DEPOSIT_AMOUNT_16
from pcapi.core.finance.models import Recredit
from pcapi.core.finance.models import RecreditType
from pcapi.core.history.models import ActionHistory
from pcapi.core.history.models import ActionType
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)


def recredit_from_previous_deposit_in_previous_account(user_id: int) -> None:
    user = db.session.scalars(select(User).where(User.id == user_id)).one()
    if not user:
        raise ValueError(f"No user with {user_id} found")

    deposit = user.deposit
    if not deposit:
        raise ValueError(f"{user} has no deposit")

    recredit = Recredit(
        deposit=deposit,
        amount=GRANTED_DEPOSIT_AMOUNT_16,
        recreditType=RecreditType.MANUAL_MODIFICATION,
        comment="(PC-39377) Recrédit de 16 ans pré-décret qui n'était pas attribué à cause d'une désynchronisation avec DN",
    )
    deposit.amount += recredit.amount
    db.session.add(recredit)
    db.session.flush()

    logger.info(f"Recrediting {user = } with {recredit.amount} euros")

    update_external_user(user)


def substract_from_deposit_because_of_past_expenses_on_another_account(
    user_id: int, user_id_with_spent_credit: int, author_id: int
) -> None:
    user = db.session.scalars(select(User).where(User.id == user_id)).one()

    deposit = user.deposit
    if not deposit:
        raise ValueError(f"{user} has no deposit")

    [
        recredit_to_delete,
    ] = [recredit for recredit in deposit.recredits if recredit.recreditType == RecreditType.RECREDIT_17]

    action_history = ActionHistory(
        actionType=ActionType.COMMENT,
        authorUserId=author_id,
        user=user,
        comment=f"(PC-39377) Suppression du crédit pré-décret {recredit_to_delete.id} de {recredit_to_delete.amount} euros déjà utilisé dans le compte doublon {user_id_with_spent_credit}",
    )
    db.session.add(action_history)

    deposit.amount -= recredit_to_delete.amount
    db.session.delete(recredit_to_delete)
    db.session.flush()

    logger.info(
        f"Deleting recredit {recredit_to_delete} that had {recredit_to_delete.amount} of {user = } that was spent in account {user_id_with_spent_credit}"
    )

    update_external_user(user)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--author", type=int)
    parser.add_argument("--user-to-recredit", type=int)
    parser.add_argument("--user-to-substract-credit", type=int)
    parser.add_argument("--user-with-spent-credit", type=int)
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    with atomic():
        if not args.not_dry:
            mark_transaction_as_invalid()
            logger.info("dry run: marked transaction as invalid")

        recredit_from_previous_deposit_in_previous_account(args.user_to_recredit)
        substract_from_deposit_because_of_past_expenses_on_another_account(
            args.user_to_substract_credit, args.user_with_spent_credit, args.author
        )

        logger.info("Finished")
