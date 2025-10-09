"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml   -f ENVIRONMENT=testing   -f BRANCH_NAME=pcharlet/pc-38196-script-update-one-venue-pricing-point   -f NAMESPACE=update_venue_pricing_point   -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

from pcapi.app import app
from pcapi.core.history import models as history_models
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db
from pcapi.utils.date import get_naive_utc_now
from pcapi.utils.db import make_timerange
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)


@atomic()
def main(not_dry: bool) -> None:
    if not not_dry:
        logger.info("Dry run mode enabled, no changes will be made to the database")
        mark_transaction_as_invalid()

    venue_id = 36361
    logger.info("Starting to update bank account for venue %d", venue_id)
    venue = db.session.query(offerers_models.Venue).filter(offerers_models.Venue.id == venue_id).one_or_none()
    if venue is None:
        logger.info("Venue not found. id: %d", venue_id)
        return
    offerers_api.link_venue_to_pricing_point(venue, venue.id, force_link=True)

    venue_bank_account_link = venue.current_bank_account_link
    if venue_bank_account_link is None:
        logger.info("No bank account linked to the venue %d", venue.id)
        return
    timespan = make_timerange(start=venue_bank_account_link.timespan.lower, end=get_naive_utc_now())
    venue_bank_account_link.timespan = timespan
    deprecated_log = history_models.ActionHistory(
        actionType=history_models.ActionType.LINK_VENUE_BANK_ACCOUNT_DEPRECATED,
        venueId=venue.id,
        bankAccountId=venue_bank_account_link.bankAccountId,
        comment="PC-38196",
    )
    db.session.add_all((deprecated_log, venue_bank_account_link))


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
