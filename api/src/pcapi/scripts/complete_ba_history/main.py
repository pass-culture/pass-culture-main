"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infra repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yaml \
  -f ENVIRONMENT_SHORT_NAME=tst \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=PC-43560-complete-existing-ba-history \
  -f NAMESPACE=complete_ba_history \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

from pcapi.core.history import models as history_models
from pcapi.models import db


logger = logging.getLogger(__name__)


def main() -> None:
    history_to_update = (
        db.session.query(history_models.ActionHistory)
        .filter(history_models.ActionHistory.actionType == history_models.ActionType.VENUE_REIMBURSEMENT_SUSPENDED)
        .all()
    )
    for history in history_to_update:
        assert history.venue
        history.offererId = history.venue.managingOffererId
        db.session.add(history)


if __name__ == "__main__":
    from pcapi.app import app

    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    main()

    if args.apply:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
