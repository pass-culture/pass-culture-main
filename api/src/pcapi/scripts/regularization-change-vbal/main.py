"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=staging \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=ogeber/pc-39120-regularization-change-venue-bank-account-links \
  -f NAMESPACE=regularization-change-vbal \
  -f SCRIPT_ARGUMENTS="";

"""

import argparse
import csv
import datetime
import logging
import os
import typing

import pcapi.core.finance.models as finance_models
import pcapi.core.offerers.models as offerers_models
from pcapi.app import app
from pcapi.core.history import models as history_models
from pcapi.models import db
from pcapi.utils import date as date_utils
from pcapi.utils import db as db_utils
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


VENUE_ID_HEADER = "venue_id"
BANK_ACCOUNT_ID_HEADER = "bank_account_id"

logger = logging.getLogger(__name__)


def _read_csv_file(filename: str) -> typing.Iterator[dict[str, str]]:
    namespace_dir = os.path.dirname(os.path.abspath(__file__))
    with open(f"{namespace_dir}/{filename}.csv", "r", encoding="utf-8") as csv_file:
        csv_rows = csv.DictReader(csv_file, delimiter=",")
        yield from csv_rows


def _get_vbal_lower_datetime(timespan_lower: str | datetime.datetime) -> datetime.datetime:
    # Handle the case where lower might be a str or a datetime according to
    # it's status regarding the session.
    # Reminder: if VenueBankAccountLink instance is 'flushed', it is still a str
    # due to 💣🤯🤬 the usage of isoformat in db_utils.make_timerange
    # Once commited, it becomes a datetime
    if isinstance(timespan_lower, str):
        return datetime.datetime.fromisoformat(timespan_lower).replace(tzinfo=None)
    return timespan_lower.replace(tzinfo=None)


def _link_venue_to_bank_account(
    bank_account: finance_models.BankAccount, venue: offerers_models.Venue
) -> offerers_models.VenueBankAccountLink | None:
    """
    copycat of ImportBankAccountMixin.link_venue_to_bank_account
    """
    if bank_account.status != finance_models.BankAccountApplicationStatus.ACCEPTED:
        logger.info("bank_account n° %d status is not accepted", bank_account.id)
        return None

    for link in bank_account.venueLinks:
        lower = _get_vbal_lower_datetime(link.timespan.lower)
        if link.timespan.upper is None and lower <= date_utils.get_naive_utc_now() and link.venue == venue:
            logger.info(
                "bank_account already linked to its venue",
                extra={
                    "bank_account_id": bank_account.id,
                    "venue_id": venue.id,
                },
            )
            return None

    if deprecated_link := venue.current_bank_account_link:
        lower_bound = deprecated_link.timespan.lower
        upper_bound = date_utils.get_naive_utc_now()
        timespan = db_utils.make_timerange(start=lower_bound, end=upper_bound)
        deprecated_link.timespan = timespan
        deprecated_log = history_models.ActionHistory(
            actionType=history_models.ActionType.LINK_VENUE_BANK_ACCOUNT_DEPRECATED,
            venueId=venue.id,
            bankAccountId=deprecated_link.bankAccountId,
        )
        db.session.add(deprecated_log)
    link = offerers_models.VenueBankAccountLink(
        bankAccount=bank_account, venue=venue, timespan=(date_utils.get_naive_utc_now(),)
    )
    created_log = history_models.ActionHistory(
        actionType=history_models.ActionType.LINK_VENUE_BANK_ACCOUNT_CREATED,
        venue=venue,
        bankAccount=bank_account,
    )
    db.session.add(created_log)
    db.session.add(link)
    db.session.flush()
    return link


@atomic()
def main(not_dry: bool, filename: str) -> None:
    if not not_dry:
        logger.info("Dry run, will be rollbacked")
        mark_transaction_as_invalid()

    rows = list(_read_csv_file(filename))

    for row in rows:
        venue_id, bank_account_id = (
            int(row[VENUE_ID_HEADER]),
            int(row[BANK_ACCOUNT_ID_HEADER]),
        )
        venue = db.session.query(offerers_models.Venue).filter(offerers_models.Venue.id == venue_id).one()
        bank_account = (
            db.session.query(finance_models.BankAccount).filter(finance_models.BankAccount.id == bank_account_id).one()
        )
        if link := _link_venue_to_bank_account(bank_account=bank_account, venue=venue):
            logger.info("Link between venue %d and bank account %d has been created", link.venueId, link.bankAccountId)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()
    filename = "vbal_update"
    main(not_dry=args.not_dry, filename=filename)

    if args.not_dry:
        logger.info("Finished")
