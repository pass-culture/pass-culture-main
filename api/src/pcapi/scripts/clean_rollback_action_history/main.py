"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=ogeber/pc-38933-rattrapage-db-historique-rollback-regul \
  -f NAMESPACE=clean_rollback_action_history \
  -f SCRIPT_ARGUMENTS="--author-id 12345";

"""

import argparse
import csv
import logging
import os
import typing

import sqlalchemy as sa
from dateutil import parser as dateutil_parser

import pcapi.core.history.models as history_models
import pcapi.core.users.models as users_models
from pcapi.app import app
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)


def _read_csv_file(filename: str) -> typing.Iterator[dict[str, str]]:
    namespace_dir = os.path.dirname(os.path.abspath(__file__))
    with open(f"{namespace_dir}/{filename}.csv", "r", encoding="utf-8") as csv_file:
        csv_rows = csv.DictReader(csv_file, delimiter=",")
        yield from csv_rows


@atomic()
def main(not_dry: bool, author: users_models.User, filename: str) -> None:
    """
    During regularization rollbacks, we forgot to change action history which was the same as regularization. So some of them are not accurate, eg. "VENUE_SOFT_DELETED" that aren't true.

    This script fetches the action history from rollbacks given their timestamp, adds comment & author where the actionType is VENUE_REGULARIZATION. It deletes the unaccurate one where the actionType VENUE_SOFT_DELETED.

    The action_history query fetches only ActionHistory without comment, just in case some lines of the csv have the same informations: eg. same origin_venue_id, destination_venue_id and same dates.
    """
    if not not_dry:
        mark_transaction_as_invalid()
        logger.info("Dry run : everything is going to be rollabcked")

    rows = list(_read_csv_file(filename))

    for row in rows:
        venue_with_siret, venue_address, timestamp = (
            int(row["jsonPayload.extra.origin_venue_id"]),
            int(row["jsonPayload.extra.destination_venue_id"]),
            dateutil_parser.isoparse(row["timestamp"]),
        )
        if venue_with_siret and venue_address:
            action_history = (
                db.session.query(history_models.ActionHistory)
                .filter(
                    history_models.ActionHistory.venueId == venue_with_siret,
                    history_models.ActionHistory.actionType == history_models.ActionType.VENUE_REGULARIZATION,
                    history_models.ActionHistory.extraData["destination_venue_id"].as_integer() == venue_address,
                    history_models.ActionHistory.authorUserId.is_(None),  # see above comment
                    history_models.ActionHistory.comment.is_(None),  # see above comment
                    sa.cast(history_models.ActionHistory.actionDate, sa.Date) == timestamp.date(),
                )
                .one_or_none()
            )
            if action_history:
                logger.info("Action history %d will be changed")
                action_history.comment = "Rollback from Venue Regularization: Venue soft delete has been reverted."
                action_history.authorUser = author
                action_history.venueId = venue_address  # we want to put action history on soft deleted venue
                action_history.actionType = history_models.ActionType.COMMENT

            db.session.query(history_models.ActionHistory).filter(
                history_models.ActionHistory.venueId == venue_with_siret,
                history_models.ActionHistory.actionType == history_models.ActionType.VENUE_SOFT_DELETED,
                history_models.ActionHistory.authorUserId.is_(None),  # just in case
                sa.cast(history_models.ActionHistory.actionDate, sa.Date) == timestamp.date(),
            ).delete()


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action=argparse.BooleanOptionalAction, default=True)
    parser.add_argument("--author-id", type=int, help="Author", required=True)
    args = parser.parse_args()

    author = db.session.query(users_models.User).filter(users_models.User.id == args.author_id).one()
    main(not_dry=args.not_dry, author=author, filename="rollback")

    if args.not_dry:
        logger.info("Finished")
