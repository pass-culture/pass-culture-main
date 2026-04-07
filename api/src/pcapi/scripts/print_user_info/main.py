"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-40971-stuck-at-profile-completion \
  -f NAMESPACE=print_user_info \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging
import os

from sqlalchemy import select

from pcapi.app import app
from pcapi.core.subscription.api import get_profile_completion_subscription_item
from pcapi.core.subscription.api import has_completed_profile_for_given_eligibility
from pcapi.core.subscription.machines import create_state_machine_to_current_state
from pcapi.core.subscription.repository import _get_completed_profile_checks
from pcapi.core.subscription.repository import get_completed_profile_check
from pcapi.core.users.models import EligibilityType
from pcapi.core.users.models import User
from pcapi.models import db
from pcapi.routes.backoffice.accounts.blueprint import _get_steps_for_tunnel
from pcapi.routes.backoffice.accounts.blueprint import _get_subscription_item_status_by_eligibility
from pcapi.routes.backoffice.accounts.blueprint import _get_tunnel_type
from pcapi.routes.backoffice.accounts.blueprint import get_eligibility_history


logger = logging.getLogger(__name__)
namespace_dir = os.environ.get("OUTPUT_DIRECTORY")
file_name = "user_info.txt"


def print_user_info(user: User) -> None:
    with open(f"{namespace_dir}/{file_name}", "w") as f:
        f.write("-" * 35 + "\n")
        logger.info("Looking into state machine")

        state_machine = create_state_machine_to_current_state(user)
        f.write(f"{type(state_machine)} state machine is currently in step {state_machine.state}\n")
        f.write("\n")

        f.write("-" * 35 + "\n")
        logger.info("Looking into fraud checks")
        f.write("All fraud checks\n")
        for fraud_check in user.beneficiaryFraudChecks:
            f.write(f"{fraud_check.id} {fraud_check.type} {fraud_check.eligibilityType} {fraud_check.status}\n")
        f.write("\n")

        f.write("All profile fraud checks\n")
        for fraud_check in _get_completed_profile_checks(user):
            f.write(f"{fraud_check.id} {fraud_check.type} {fraud_check.eligibilityType} {fraud_check.status}\n")
        f.write("\n")

        f.write(f"User {user.id} has eligibility {user.eligibility}\n")
        for eligibility in [EligibilityType.UNDERAGE, EligibilityType.AGE18, EligibilityType.AGE17_18]:
            f.write(f"User has {get_profile_completion_subscription_item(user, eligibility) = } for {eligibility = }\n")
            f.write(
                f"User has {has_completed_profile_for_given_eligibility(user, eligibility) = } profile for {eligibility = }\n"
            )
            f.write(f"User has {get_completed_profile_check(user, eligibility) = } for {eligibility = }\n")
        f.write("\n")

        f.write("-" * 35 + "\n")
        logger.info("Looking into backoffice tunnel")

        eligibility_history = get_eligibility_history(user)
        f.write(f"{eligibility_history = }\n")
        for eligibility_str, subscription_history in eligibility_history.items():
            f.write(f"{eligibility_str = }, {subscription_history.__dict__}\n")

        subscription_item_status = _get_subscription_item_status_by_eligibility(eligibility_history)
        f.write(f"{subscription_item_status = }\n")
        for eligibility_str, step_status_by_type in subscription_item_status.items():
            for step_type, step_status in step_status_by_type.items():
                f.write(f"{eligibility_str = }, {step_type = }, {step_status = }\n")

        tunnel_type = _get_tunnel_type(user)
        f.write(f"{tunnel_type = }\n")

        steps = _get_steps_for_tunnel(user, tunnel_type, subscription_item_status)
        f.write(f"{steps = }\n")
        for step in steps:
            f.write(f"{step = }\n")


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--user-id", type=int)
    args = parser.parse_args()

    user = db.session.scalars(select(User).where(User.id == args.user_id)).one()
    print_user_info(user)
