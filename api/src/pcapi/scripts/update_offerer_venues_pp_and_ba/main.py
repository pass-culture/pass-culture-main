"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml   -f ENVIRONMENT=testing   -f BRANCH_NAME=pcharlet/pc-38290-script-prepare-offerer-for-regul   -f NAMESPACE=update_offerer_venues_pp_and_ba   -f SCRIPT_ARGUMENTS="";

"""

import argparse
import logging

from pcapi.app import app
from pcapi.core.history import models as history_models
from pcapi.core.offerers import api as offerers_api
from pcapi.core.offerers import models as offerers_models
from pcapi.models import db
from pcapi.utils.date import get_naive_utc_now
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)

OFFERER_ID = 7790
PRICING_POINT_VENUE_ID = 18698


@atomic()
def main(not_dry: bool) -> None:
    if not not_dry:
        logger.info("Dry run mode enabled, no changes will be made to the database")
        mark_transaction_as_invalid()

    offerer = db.session.query(offerers_models.Offerer).filter(offerers_models.Offerer.id == OFFERER_ID).first()
    if offerer is None:
        logger.info("No offerer found for id %s", OFFERER_ID)
        return

    pricing_point = (
        db.session.query(offerers_models.Venue)
        .filter(
            offerers_models.Venue.id == PRICING_POINT_VENUE_ID, offerers_models.Venue.managingOffererId == OFFERER_ID
        )
        .first()
    )
    if pricing_point is None:
        logger.info("No venue pricing point found for id %s", PRICING_POINT_VENUE_ID)
        return
    assert pricing_point.current_bank_account

    venues_to_update = [venue for venue in offerer.managedVenues if venue.id != PRICING_POINT_VENUE_ID]
    for venue in venues_to_update:
        offerers_api.link_venue_to_pricing_point(venue, pricing_point.id, force_link=True)

        venue_bank_account_link = venue.current_bank_account_link
        if venue_bank_account_link is None:
            venue_bank_account_link = offerers_models.VenueBankAccountLink(
                venue=venue,
                bankAccount=pricing_point.current_bank_account,
                timespan=(get_naive_utc_now(),),
            )
            log = history_models.ActionHistory(
                actionType=history_models.ActionType.LINK_VENUE_BANK_ACCOUNT_CREATED,
                venueId=venue.id,
                bankAccountId=pricing_point.current_bank_account.id,
                comment="PC-38290",
            )
            db.session.add_all((log, venue_bank_account_link))
        else:
            logger.info("Venue %d linked to bank account %s", venue.id, venue_bank_account_link.bankAccount.id)


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    main(not_dry=args.not_dry)

    if args.not_dry:
        logger.info("Finished")
        db.session.commit()
    else:
        logger.info("Finished dry run, rollback")
        db.session.rollback()
