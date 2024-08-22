import argparse
import logging
import os
import sys

from pcapi.core.offerers.models import Venue
from pcapi.core.offers.api import batch_update_offers
from pcapi.core.offers.models import Offer
from pcapi.core.offers.repository import get_synchronized_offers_with_provider_for_venue
from pcapi.core.providers.models import Provider
from pcapi.flask_app import app
from pcapi.utils.chunks import get_chunks
from pcapi.workers.update_all_offers_active_status_job import update_venue_synchronized_offers_active_status_job


logger = logging.getLogger(__name__)


def usage() -> None:
    print("Usage:")
    print(f"{os.path.relpath(__file__)} <venue_id> <provider_id>")
    print("")


def check_resources_exists(venue_id: int, provider_id: int) -> None:
    if not Venue.query.get(venue_id):
        logger.info("venue #%d does not exist", venue_id)
        sys.exit(-1)

    if not Provider.query.get(provider_id):
        logger.info("provider #%d does not exist", provider_id)
        sys.exit(-1)


def push_async_job(venue_id: int, provider_id: int) -> None:
    logger.info("starting deactivation job for venue #%d and provider #%d", venue_id, provider_id)

    update_venue_synchronized_offers_active_status_job.delay(venue_id, provider_id, False)

    logger.info("deactivation job for venue #%d and provider #%d registered", venue_id, provider_id)


def run_task(venue_id: int, provider_id: int) -> None:
    base_query = get_synchronized_offers_with_provider_for_venue(venue_id, provider_id)

    total_ids = [row[0] for row in base_query.with_entities(Offer.id).yield_per(10_000)]
    logger.info("script: batch deactivation: all ids have been loaded (total %d)", len(total_ids))

    for idx, ids in enumerate(get_chunks(total_ids, 500), start=1):
        query = base_query.filter(Offer.id.in_(ids))

        batch_update_offers(query, {"isActive": False})

        logger.info(
            "script: batch deactivation: round %d, %d offers deactivated for venue #%d", idx, len(ids), venue_id
        )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--runner", choices=["sync", "async"], required=True)
    parser.add_argument("venue_id", type=int)
    parser.add_argument("provider_id", type=int)

    args = parser.parse_args()

    with app.app_context():
        check_resources_exists(args.venue_id, args.provider_id)

        if args.runner == "async":
            push_async_job(args.venue_id, args.provider_id)
        else:
            run_task(args.venue_id, args.provider_id)
