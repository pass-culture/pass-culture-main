"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=ogeber/pc-38544-script-pp \
  -f NAMESPACE=change_venue_pricing_point \
  -f SCRIPT_ARGUMENTS="--venue-id 38034";

"""

import argparse
import logging

import pcapi.utils.db as db_utils
from pcapi.app import app
from pcapi.core.history import models as history_models
from pcapi.core.offerers.api import link_venue_to_pricing_point
from pcapi.core.offerers.models import Venue
from pcapi.models import db
from pcapi.utils import date as date_utils
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)


@atomic()
def main(venue_id: int, not_dry: bool = False) -> None:
    if not not_dry:
        logger.info("Script has been run dry, will be rollbacked")
        mark_transaction_as_invalid()

    now = date_utils.get_naive_utc_now()
    venue = db.session.query(Venue).filter(Venue.id == venue_id).one()
    current_vbal = venue.current_bank_account_link

    # end current vbal
    if current_vbal:
        current_vbal.timespan = db_utils.make_timerange(current_vbal.timespan.lower, now)
        deprecated_log = history_models.ActionHistory(
            actionType=history_models.ActionType.LINK_VENUE_BANK_ACCOUNT_DEPRECATED,
            venueId=venue.id,
            bankAccountId=current_vbal.bankAccountId,
            comment="(PC-38544)",
        )

    # end current vppl and create new vppl
    link_venue_to_pricing_point(
        venue=venue,
        pricing_point_id=venue_id,
        force_link=True,
    )
    db.session.add_all([current_vbal, deprecated_log])


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--not-dry", action="store_true")
    parser.add_argument("--venue-id", required=True)
    args = parser.parse_args()

    main(venue_id=int(args.venue_id), not_dry=args.not_dry)

    if args.not_dry:
        logger.info("Finished")
