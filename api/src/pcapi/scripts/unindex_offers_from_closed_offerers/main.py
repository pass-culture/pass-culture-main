import argparse
import itertools
import logging
import time

import sqlalchemy as sa
from algoliasearch.search_client import SearchClient
from algoliasearch.search_client import SearchIndex

from pcapi import settings
from pcapi.app import app
from pcapi.core.offerers.models import Offerer
from pcapi.core.offerers.models import Venue
from pcapi.core.offers.models import Offer
from pcapi.core.search import _get_backend
from pcapi.core.search import get_base_query_for_offer_indexation
from pcapi.core.search import get_last_x_days_booking_count_by_offer
from pcapi.core.search.backends.algolia import AlgoliaBackend
from pcapi.models import db
from pcapi.models.validation_status_mixin import ValidationStatus


logger = logging.getLogger(__name__)


def get_venue_ids_from_closed_offerers() -> list[int]:
    query = sa.select(Venue.id).join(Offerer).where(Offerer.validationStatus == ValidationStatus.CLOSED)
    return db.session.scalars(query).all()


def fetch_object_ids_by_facet_pattern(index: SearchIndex, facet_name: str, value: str) -> list[int]:
    search_parameters = {
        "facetFilters": [f"{facet_name}:{value}"],
        "attributesToRetrieve": ["objectID"],
        "hitsPerPage": 1000,
    }
    object_ids = []
    page = 0

    try:
        while True:
            search_parameters["page"] = page
            results = index.search("", search_parameters)
            hits = results.get("hits", [])
            object_ids.extend(int(hit["objectID"]) for hit in hits)

            if page >= results.get("nbPages", 0) - 1 or not hits:
                break
            page += 1

        return object_ids
    except Exception as e:
        logger.error(f"An error occurred while fetching from Algolia: {e}")
        return []


def reindex_offer_ids(backend: AlgoliaBackend, offer_ids: list[int]) -> None:
    to_add = []
    to_delete_ids = []
    offers = get_base_query_for_offer_indexation().filter(Offer.id.in_(offer_ids))

    for offer in offers:
        if offer and offer.is_eligible_for_search:
            to_add.append(offer)
        else:
            to_delete_ids.append(offer.id)

    for offer_id in offer_ids:
        if offer_id not in to_add:
            to_delete_ids.append(offer_id)

    last_x_days_bookings_count_by_offer = get_last_x_days_booking_count_by_offer(to_add)
    backend.index_offers(to_add, last_x_days_bookings_count_by_offer)
    backend.unindex_offer_ids(set(to_delete_ids))


def reindex_offers_by_venue(reindex: bool, cool_down: int = 0) -> None:
    client = SearchClient.create(settings.ALGOLIA_APPLICATION_ID, settings.ALGOLIA_API_KEY)
    index = client.init_index(settings.ALGOLIA_OFFERS_INDEX_NAME)
    backend = _get_backend()

    venue_ids = get_venue_ids_from_closed_offerers()

    if not venue_ids:
        logger.info("No venues found to process.")
        return

    logger.info(f"Found {len(venue_ids)} venues to reindex.")

    # Algolia limits results to 1000 per search.
    # If a venue has >1000 offers, we process the first 1000 and
    # the loop will need to be re-run.
    should_reindex_offers = {venue_id: True for venue_id in venue_ids}
    while any(should_reindex_offers.values()):
        for venue_id in venue_ids:
            if not should_reindex_offers[venue_id]:
                continue

            offer_ids = fetch_object_ids_by_facet_pattern(index, "venue.id", venue_id)
            if not offer_ids:
                logger.info(f"No offers found for venue {venue_id}")
                should_reindex_offers[venue_id] = False
                continue

            if reindex:
                logger.info(f"Reindexing {len(offer_ids)} offers for venue {venue_id}")
                for batch in itertools.batched(offer_ids, 1000):
                    reindex_offer_ids(backend, batch)
            else:
                logger.info(f"[DRY RUN] Would reindex {len(offer_ids)} offers for venue {venue_id}")
                should_reindex_offers[venue_id] = False

        # Let Algolia asynchronously index offers before re-fetching
        time.sleep(cool_down)


if __name__ == "__main__":
    app.app_context().push()
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--reindex", action="store_true")
    parser.add_argument("-c", "--cool-down", default=0, type=int)
    args = parser.parse_args()

    reindex_offers_by_venue(args.reindex, args.cool_down)
