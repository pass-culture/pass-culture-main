"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-40201-move-activation \
  -f NAMESPACE=move_subscription_events \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import csv
import logging
import os

from sqlalchemy import select

from pcapi.app import app
from pcapi.core.external.attributes.api import update_external_user
from pcapi.core.subscription import machines as subscription_machines
from pcapi.core.subscription.api import activate_beneficiary_if_no_missing_step
from pcapi.core.subscription.api import move_subscription_fraud_checks
from pcapi.core.users.models import EligibilityType
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)
namespace_dir = os.path.dirname(os.path.abspath(__file__))


def move_subscription_and_credit_destination_account(
    from_user: User, to_user: User, author_id: int | None, should_update_external_user: bool = False
) -> None:
    move_subscription_fraud_checks(from_user, to_user, eligibility=EligibilityType.AGE18, author_id=author_id)

    if not to_user.phoneNumber:
        to_user.phoneNumber = from_user.phoneNumber

    try:
        was_beneficiary_credited = activate_beneficiary_if_no_missing_step(to_user)
    except Exception as e:
        logger.error(
            "Error during beneficiary activation for user %s, manual review is needed",
            to_user.id,
            extra={"exc": str(e)},
        )
        return

    if was_beneficiary_credited:
        deposit = to_user.deposit
        if deposit:
            logger.info("Beneficiary %s was credited %s with amount %.2f", to_user.id, deposit.type, deposit.amount)
    else:
        subscription_state_machine = subscription_machines.create_state_machine_to_current_state(to_user)
        logger.warning(
            "Beneficiary %s was not credited, with status %s for %s subscription",
            to_user.id,
            subscription_state_machine.state.value,
            type(subscription_state_machine),
        )

    if should_update_external_user:
        update_external_user(to_user)


def read_user_ids_from_csv(file_name: str) -> list[tuple[int, int]]:
    args_list = []
    with open(f"{namespace_dir}/{file_name}", encoding="utf-8") as csv_file:
        reader = csv.DictReader(csv_file)
        for row in reader:
            from_user_id = int(row["from_user_id"])
            to_user_id = int(row["to_user_id"])
            args_list.append((from_user_id, to_user_id))

    return args_list


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--author-id", type=int, default=None)
    args = parser.parse_args()

    with atomic():
        if not args.apply:
            mark_transaction_as_invalid()
            logger.info("dry run, rollbacking at the end of the transaction")

        for from_user_id, to_user_id in read_user_ids_from_csv("users_to_move_subscription.csv"):
            from_user = db.session.scalars(select(User).where(User.id == from_user_id)).one()
            to_user = db.session.scalars(select(User).where(User.id == to_user_id)).one()
            move_subscription_and_credit_destination_account(
                from_user, to_user, args.author_id, should_update_external_user=args.apply
            )
