"""
Job console documentation here: https://www.notion.so/passcultureapp/Documentation-Job-Console-769beeacd5a146de9c97b6f8ee544276

You can start the job from the infrastructure repository with github cli :

gh workflow run on_dispatch_pcapi_console_job.yml \
  -f ENVIRONMENT=testing \
  -f RESOURCES="512Mi/.5" \
  -f BRANCH_NAME=ogeber/pc-38687-fix-pricing-point \
  -f NAMESPACE=fix_pricing_point \
  -f SCRIPT_ARGUMENTS="--venue-id 123 --pricing-point-id 123 --not-dry";

"""

import argparse
import logging

from pcapi.app import app
from pcapi.core.offerers.api import link_venue_to_pricing_point
from pcapi.core.offerers.models import Venue
from pcapi.models import db
from pcapi.utils.transaction_manager import atomic
from pcapi.utils.transaction_manager import mark_transaction_as_invalid


logger = logging.getLogger(__name__)


@atomic()
def main(venue_id: int, pricing_point_id: int, not_dry: bool = False) -> None:
    if not not_dry:
        logger.info("Script has been run dry, will be rollbacked")
        mark_transaction_as_invalid()

    venue = db.session.query(Venue).execution_options(include_deleted=True).filter(Venue.id == venue_id).one()
    link_venue_to_pricing_point(
        venue=venue,
        pricing_point_id=pricing_point_id,
        force_link=True,
    )


if __name__ == "__main__":
    app.app_context().push()

    parser = argparse.ArgumentParser()
    parser.add_argument("--venue-id", type=int, required=True)
    parser.add_argument("--pricing-point-id", type=int, required=True)
    parser.add_argument("--not-dry", action="store_true")
    args = parser.parse_args()

    main(venue_id=args.venue_id, pricing_point_id=args.pricing_point_id, not_dry=args.not_dry)

    if args.not_dry:
        logger.info("Finished")
