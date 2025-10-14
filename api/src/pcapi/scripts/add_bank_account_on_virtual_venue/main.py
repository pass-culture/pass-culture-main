"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml   -f ENVIRONMENT=testing   -f BRANCH_NAME=pcharlet/pc-38354-add-bank-account-on-virtual-venue   -f NAMESPACE=add_bank_account_on_virtual_venue   -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

from pcapi.app import app
from pcapi.core.finance import models as finance_models
from pcapi.core.history import models as history_models
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db
from pcapi.utils.date import get_naive_utc_now
from pcapi.utils.db import make_timerange
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)

VENUE_ID = 485
BANK_ACCOUNT_ID = 50836


@atomic()
def main(not_dry: bool) -> None:
    if not not_dry:
        logger.info("Dry run mode enabled, no changes will be made to the database")
        mark_transaction_as_invalid()

    venue = db.session.query(offerers_models.Venue).filter(offerers_models.Venue.id == VENUE_ID).one()
    venue_bank_account_link = venue.current_bank_account_link
    if venue_bank_account_link:
        timespan = make_timerange(start=venue_bank_account_link.timespan.lower, end=get_naive_utc_now())
        venue_bank_account_link.timespan = timespan
        deprecated_log = history_models.ActionHistory(
            actionType=history_models.ActionType.LINK_VENUE_BANK_ACCOUNT_DEPRECATED,
            venueId=venue.id,
            bankAccountId=venue_bank_account_link.bankAccountId,
            comment="PC-38354",
        )
        db.session.add(deprecated_log)

    bank_account = (
        db.session.query(finance_models.BankAccount).filter(finance_models.BankAccount.id == BANK_ACCOUNT_ID).one()
    )
    link = offerers_models.VenueBankAccountLink(
        bankAccount=bank_account,
        venue=venue,
        timespan=(get_naive_utc_now(),),
    )
    logger.info("Ajout du compte bancaire %d pour la venue %d", bank_account.id, venue.id)
    action_history = history_models.ActionHistory(
        actionType=history_models.ActionType.LINK_VENUE_BANK_ACCOUNT_CREATED,
        venueId=venue.id,
        bankAccountId=bank_account.id,
        comment="PC-38354",
    )
    db.session.add_all((link, action_history))


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
        logger.info("Finished dry run, rollback")
