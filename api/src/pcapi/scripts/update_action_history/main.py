"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276
Assumed path to the script (copy-paste in github actions):

https://github.com/pass-culture/pass-culture-main/blob/pcharlet/pc-37366-update-action-history/api/src/pcapi/scripts/update_action_history/main.py

"""

import argparse
import csv
import logging
import os
import typing

from pcapi.app import app
from pcapi.core.history import models as history_models
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)


def _read_csv_file() -> typing.Iterator[dict[str, str]]:
    namespace_dir = os.path.dirname(os.path.abspath(__file__))
    with open(f"{namespace_dir}/ajout_bank_account-10-07-prod.csv", "r", encoding="utf-8") as csv_file:
        csv_rows = csv.DictReader(csv_file, delimiter=",")
        yield from csv_rows


@atomic()
def main(not_dry: bool) -> None:
    if not not_dry:
        mark_transaction_as_invalid()
    logs = _read_csv_file()
    for log in logs:
        venue_id = int(log["jsonPayload.message"].split()[2])
        bank_account_id = int(log["jsonPayload.message"].split()[7])
        action_history = (
            db.session.query(history_models.ActionHistory)
            .filter(
                history_models.ActionHistory.actionType == history_models.ActionType.VENUE_REGULARIZATION,
                history_models.ActionHistory.venueId == venue_id,
                history_models.ActionHistory.bankAccountId == bank_account_id,
            )
            .one_or_none()
        )
        if action_history:
            action_history.actionType = history_models.ActionType.LINK_VENUE_BANK_ACCOUNT_CREATED
            db.session.add(action_history)
            logger.info("Action history for venue %d and bank account %d updated", venue_id, bank_account_id)
        else:
            logger.info("No action history found for venue %d and bank account %d", venue_id, bank_account_id)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    main(not_dry=args.not_dry)

    if args.not_dry:
        logger.info("Finished")
    else:
        db.session.rollback()
        logger.info("Finished dry run, rollback")
