"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/PC-36344-extend-deposits/api/src/pcapi/scripts/extend_deposit/main.py

"""

import argparse
import logging
from datetime import datetime

from dateutil.relativedelta import relativedelta
from sqlalchemy.orm import selectinload

from pcapi.app import app
from pcapi.core.external.attributes.api import update_external_user
from pcapi.core.history.models import ActionHistory
from pcapi.core.history.models import ActionType
from pcapi.core.users.models import User
from pcapi.models import db


logger = logging.getLogger(__name__)

# AUTHOR_ID = 6721024 # Dan
AUTHOR_ID = 1633706  # Corentin


def extend_user_deposit(user_id: int, not_dry: bool) -> None:
    user = db.session.query(User).filter(User.id == user_id).options(selectinload(User.deposits)).one()

    deposit = user.deposit
    if not deposit:
        return

    in_ninety_days = datetime.utcnow() + relativedelta(days=90)
    deposit.expirationDate = in_ninety_days

    action_log = ActionHistory(
        actionType=ActionType.COMMENT,
        user=user,
        authorUserId=AUTHOR_ID,
        comment=f"(PC-36344) Extension manuelle du crédit {deposit.id} de 30 jours",
    )
    db.session.add(action_log)

    if not_dry:
        update_external_user(user)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--user-id", type=int)
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    extend_user_deposit(user_id=args.user_id, not_dry=args.not_dry)

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
