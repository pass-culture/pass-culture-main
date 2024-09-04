import argparse
import logging
from math import ceil

import sqlalchemy as sa

from pcapi.app import app
from pcapi.core.offerers import api as offerers_api
from pcapi.repository import db


BATCH_SIZE = 1000

logger = logging.getLogger(__name__)


def main() -> None:
    with app.app_context():
        parser = argparse.ArgumentParser()
        parser.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=True)
        parser.add_argument("--start-from-batch", type=int, default=1)
        parser.add_argument("--batch-size", type=int, default=BATCH_SIZE)
        args = parser.parse_args()

        count_before_match = offerers_api.count_permanent_venues_with_accessibility_provider()
        logger.info("Number of venue synchronized before matching %d", count_before_match)
        venues_list = offerers_api.get_permanent_venues_without_accessibility_provider()
        num_batches = ceil(len(venues_list) / args.batch_size)
        if args.start_from_batch > num_batches:
            logger.info("Start from batch must be less than %d", num_batches)
            return

        start_batch_index = args.start_from_batch - 1
        count_after_match = 0
        for i in range(start_batch_index, num_batches):
            batch_start = i * args.batch_size
            batch_end = (i + 1) * args.batch_size
            for venue in venues_list[batch_start:batch_end]:
                offerers_api.set_accessibility_provider_id(venue)  # try to find a match at acceslibre
                if venue.external_accessibility_id:
                    count_after_match += 1
            if not args.dry_run:
                try:
                    db.session.commit()
                except sa.exc.SQLAlchemyError:
                    logger.exception("Could not update batch %d", i + 1)
                    db.session.rollback()
                count_after_match = offerers_api.count_permanent_venues_with_accessibility_provider()

        logger.info("Matching complete, %s new match found", count_after_match - count_before_match)


if __name__ == "__main__":
    main()
