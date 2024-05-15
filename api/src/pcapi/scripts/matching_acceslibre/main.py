import argparse
import logging
from math import ceil

import sqlalchemy as sa

import pcapi.connectors.acceslibre as accessibility_provider
from pcapi.core.offerers import api as offerers_api
from pcapi.flask_app import app
from pcapi.models import db


logger = logging.getLogger(__name__)
BATCH_SIZE = 1000


def acceslibre_matching(dry_run: bool = False, start_from_batch: int = 1) -> None:
    """
    For all permanent venues, we are looking for a match at acceslibre

    If we use the --start-from-batch option, it will start synchronization from the given batch number
    Use case: synchronization has failed with message "Could not update batch <n>"
    """
    venues_list = offerers_api.get_permanent_venues_without_accessibility_provider()
    num_batches = ceil(len(venues_list) / BATCH_SIZE)
    if start_from_batch > num_batches:
        logger.info("Start from batch must be less than %d", num_batches)
        return

    results_list = []

    for activity in accessibility_provider.AcceslibreActivity:
        if results_by_activity := accessibility_provider.find_new_entries_by_activity(activity):
            results_list.extend(results_by_activity)

    start_batch_index = start_from_batch - 1
    for i in range(start_batch_index, num_batches):
        batch_start = i * BATCH_SIZE
        batch_end = (i + 1) * BATCH_SIZE
        offerers_api.match_venue_with_new_entries(venues_list[batch_start:batch_end], results_list)

        if not dry_run:
            try:
                db.session.commit()
            except sa.exc.SQLAlchemyError:
                logger.exception("Could not update batch %d", i + 1)
                db.session.rollback()
        else:
            db.session.rollback()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument("--start-from-batch", type=int, default=1)
    args = parser.parse_args()
    with app.app_context():
        acceslibre_matching(dry_run=args.dry_run, start_from_batch=args.start_from_batch)


if __name__ == "__main__":
    main()
