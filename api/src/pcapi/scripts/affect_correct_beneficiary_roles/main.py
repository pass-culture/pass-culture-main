"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions): 

https://github.com/pass-culture/pass-culture-main/blob/pc-35213/api/src/pcapi/scripts/affect_correct_beneficiary_roles/main.py

"""

import argparse
import datetime
import logging

from dateutil.relativedelta import relativedelta

from pcapi.app import app
from pcapi.core.external.attributes.api import update_external_user
from pcapi.core.finance.models import Deposit
from pcapi.core.finance.models import DepositType
from pcapi.core.users.models import User
from pcapi.core.users.models import UserRole
from pcapi.models import db


logger = logging.getLogger(__name__)


def main(not_dry: bool) -> None:
    eighteen_years_ago = datetime.date.today() - relativedelta(years=18)
    query = User.query.join(User.deposits).filter(
        User.validatedBirthDate <= eighteen_years_ago,  # Only over 18yo users are concerned
        User.roles.contains([UserRole.UNDERAGE_BENEFICIARY]),
        Deposit.type == DepositType.GRANT_17_18,
    )

    for user in query:  # there are few enough cases to not bother with pagination
        # Double check things, tis condition should always be true, considering the query
        if user.received_pass_18_v3 and user.has_underage_beneficiary_role:
            user.remove_underage_beneficiary_role()
            user.add_beneficiary_role()

            logger.info("User %s has been updated", user.id)
        else:
            logger.info("User %s is already correct, %s %s", user.id, user.roles, user.deposit.type)

        if not_dry:
            update_external_user(user)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    main(not_dry=args.not_dry)

    if args.not_dry:
        db.session.commit()
        logger.info("Finished")
    else:
        db.session.rollback()
        logger.info("Finished dry run, rollback")
