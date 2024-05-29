import argparse
import logging

import pcapi.core.bookings.api as booking_api  # pylint: disable=unused-import
from pcapi.core.offerers import api as offerers_api


logger = logging.getLogger(__name__)
BATCH_SIZE = 1000

if __name__ == "__main__":
    from pcapi.flask_app import app

    with app.app_context():
        logger.info("PC-29546 : Starting matching acceslibre")

        parser = argparse.ArgumentParser(
            description="Fetch last 7 days new entries at acceslibre and check for match with our venues"
        )
        parser.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=True)
        parser.add_argument("--start-from-batch", type=int, default=1)
        parser.add_argument("--batch-size", type=int, default=BATCH_SIZE)

        args = parser.parse_args()

        count_before_match = offerers_api.count_permanent_venues_with_accessibility_provider()
        offerers_api.acceslibre_matching(
            batch_size=args.batch_size, dry_run=args.dry_run, start_from_batch=args.start_from_batch
        )
        count_after_match = offerers_api.count_permanent_venues_with_accessibility_provider()

        logger.info("PC-29546 : Matching complete, %s new match found", count_after_match - count_before_match)
