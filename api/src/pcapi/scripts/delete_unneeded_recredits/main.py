"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-39146-delete-bad-recredits \
  -f NAMESPACE=delete_unneeded_recredits \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

from sqlalchemy import select
from sqlalchemy.orm import joinedload

from pcapi.app import app
from pcapi.core.finance.models import Deposit
from pcapi.core.finance.models import Recredit
from pcapi.core.history.models import ActionHistory
from pcapi.core.history.models import ActionType
from pcapi.models import db


logger = logging.getLogger(__name__)


AUTHOR_ID = 6721024
RECREDITS_ID_TO_DELETE = [74990, 141477]


def delete_unneeded_recredits(recredits_id: list[int]) -> None:
    """
    Due to a bug, some young beneficiaries were given the same recredit twice.
    Those recredits pollute the database, preventing the creation of a unique index on the Recredit table.
    Since those credits are already spent, we can safely delete them (without touching the deposit).
    """
    recredits_to_delete_stmt = (
        select(Recredit)
        .where(Recredit.id.in_(recredits_id))
        .options(joinedload(Recredit.deposit).joinedload(Deposit.user))
    )
    for recredit in db.session.scalars(recredits_to_delete_stmt):
        action_log = ActionHistory(
            actionType=ActionType.COMMENT,
            user=recredit.deposit.user,
            authorUserId=AUTHOR_ID,
            comment=f"(PC-39146) Suppression du mauvais recrédit {recredit.id} de type {recredit.recreditType}",
        )
        db.session.add(action_log)

        db.session.delete(recredit)
        logger.info("deleted recredit %s of user %s", recredit.id, recredit.deposit.user.id)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    parser.add_argument("--recredit-ids", nargs="+", type=int)
    args = parser.parse_args()

    recredit_ids_to_delete = args.recredit_ids or RECREDITS_ID_TO_DELETE
    logger.info(f"{recredit_ids_to_delete = }")
    delete_unneeded_recredits(recredit_ids_to_delete)

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
