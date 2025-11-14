"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=ogeber/pc-38691-add-bank-account-on-virtual-venue \
  -f NAMESPACE=add_bank_account_on_virtual_venues \
  -f SCRIPT_ARGUMENTS="--venue-id 123 --bank-account-id 123 --not-dry";

"""

import argparse
import logging

import pcapi.utils.db as db_utils
from pcapi.app import app
from pcapi.core.finance import models as finance_models
from pcapi.core.history import models as history_models
from pcapi.core.offerers import models as offerers_models
from pcapi.core.offerers.models import Venue
from pcapi.models import db
from pcapi.utils import date as date_utils
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)


def _link_venue_to_bank_account(bank_account: finance_models.BankAccount, venue: "Venue") -> None:
    if bank_account.status != finance_models.BankAccountApplicationStatus.ACCEPTED:
        logger.info("Bank account status is not ACCEPTED ")

    if bank_account.venueLinks:
        current_link = bank_account.current_link
        assert current_link  # helps mypy
        if current_link.venue == venue:
            logger.info(
                "bank_account already linked to its venue",
                extra={
                    "bank_account_id": bank_account.id,
                    "venue_id": venue.id,
                },
            )
            return None

    if venue.current_bank_account_link:
        deprecated_link = venue.current_bank_account_link
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
        comment="(PC-38691)",
    )
    db.session.add(created_log)
    db.session.add(link)


@atomic()
def main(venue_id: int, bank_account_id: int, not_dry: bool = False) -> None:
    if not not_dry:
        logger.info("Script has been run dry, will be rollbacked")
        mark_transaction_as_invalid()

    venue = db.session.query(Venue).filter(Venue.id == venue_id).one()
    bank_account = (
        db.session.query(finance_models.BankAccount)
        .filter(
            finance_models.BankAccount.id == bank_account_id,
        )
        .one()
    )
    _link_venue_to_bank_account(bank_account=bank_account, venue=venue)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    parser.add_argument("--venue-id", type=int, required=True)
    parser.add_argument("--bank-account-id", type=int, required=True)
    args = parser.parse_args()

    main(
        venue_id=args.venue_id,
        bank_account_id=args.bank_account_id,
        not_dry=args.not_dry,
    )

    if args.not_dry:
        logger.info("Finished")
